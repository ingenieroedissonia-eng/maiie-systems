"""
Modulo: Vector Store
Capa: Infrastructure

Descripcion:
Implementacion de un almacen de vectores que utiliza google-generativeai para
la generacion de embeddings y numpy para calculos de similitud coseno.

Responsabilidades:
- Configurar y utilizar el cliente de Google Generative AI.
- Generar embeddings para el contenido de los documentos.
- Realizar busquedas de similitud entre un texto de consulta y los documentos almacenados.
- Interactuar con un repositorio de documentos para la persistencia.

Version: 1.0.0
"""
import logging
import os
from typing import List, Tuple

import google.generativeai as genai
import numpy as np

from core.document import Document
from core.exceptions import EmbeddingGenerationError, SimilarityCalculationError
from core.repository import DocumentRepository

# Configurar el logger para este modulo
logger = logging.getLogger(__name__)

# Se recomienda configurar el nivel de logging en la aplicacion principal
# logging.basicConfig(level=logging.INFO)

class VectorStore:
    """
    Gestiona la generacion de embeddings y la busqueda por similitud de documentos.
    """

    def __init__(self, document_repository: DocumentRepository, model_name: str = "models/text-embedding-004"):
        """
        Inicializa el VectorStore.

        Args:
            document_repository (DocumentRepository): El repositorio para acceder a los documentos.
            model_name (str): El nombre del modelo de embedding a utilizar.
        """
        self.document_repository = document_repository
        self.model_name = model_name
        try:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("La variable de entorno GOOGLE_API_KEY no esta configurada.")
            genai.configure(api_key=api_key)
            logger.info("Cliente de Google Generative AI configurado exitosamente.")
        except ValueError as e:
            logger.error("Error de configuracion de Google Generative AI: %s", e)
            raise e
        except Exception as e:
            logger.error("Ocurrio un error inesperado durante la configuracion de Google Generative AI: %s", e)
            raise ConnectionError("No se pudo configurar el cliente de Google Generative AI.") from e

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Genera un embedding para un texto dado.

        Args:
            text (str): El texto para el cual generar el embedding.

        Returns:
            List[float]: El vector de embedding generado.

        Raises:
            EmbeddingGenerationError: Si ocurre un error durante la generacion del embedding.
        """
        if not text or not text.strip():
            logger.warning("Se intento generar un embedding para un texto vacio.")
            raise ValueError("El contenido del texto no puede estar vacio.")
        try:
            result = genai.embed_content(model=self.model_name, content=text)
            return result['embedding']
        except Exception as e:
            logger.error("Error al generar embedding con la API de Google: %s", e)
            raise EmbeddingGenerationError(f"Fallo la generacion de embedding para el texto: '{text[:30]}...'") from e

    def add_document(self, document: Document) -> Document:
        """
        Genera el embedding para un documento y lo guarda en el repositorio.

        Args:
            document (Document): El documento a procesar y guardar.

        Returns:
            Document: El documento actualizado con su embedding.
        """
        logger.info("Generando embedding para el documento con id: %s", document.id)
        embedding = self._generate_embedding(document.content)
        document.embedding = embedding
        self.document_repository.save(document)
        logger.info("Documento con id %s guardado con su embedding.", document.id)
        return document

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calcula la similitud coseno entre dos vectores.

        Args:
            vec1 (List[float]): El primer vector.
            vec2 (List[float]): El segundo vector.

        Returns:
            float: El valor de la similitud coseno (entre -1 y 1).

        Raises:
            SimilarityCalculationError: Si los vectores no son validos para el calculo.
        """
        try:
            np_vec1 = np.array(vec1)
            np_vec2 = np.array(vec2)

            if np_vec1.shape != np_vec2.shape:
                raise ValueError("Los vectores deben tener la misma dimension.")

            dot_product = np.dot(np_vec1, np_vec2)
            norm_vec1 = np.linalg.norm(np_vec1)
            norm_vec2 = np.linalg.norm(np_vec2)

            if norm_vec1 == 0 or norm_vec2 == 0:
                logger.warning("Calculo de similitud con un vector de norma cero.")
                return 0.0

            similarity = dot_product / (norm_vec1 * norm_vec2)
            return float(similarity)
        except (ValueError, TypeError) as e:
            logger.error("Error en el calculo de similitud coseno: %s", e)
            raise SimilarityCalculationError("Error en los datos de entrada para el calculo de similitud.") from e

    def search_similar(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """
        Busca los documentos mas similares a una consulta de texto.

        Args:
            query (str): El texto de la consulta.
            top_k (int): El numero de documentos mas similares a devolver.

        Returns:
            List[Tuple[Document, float]]: Una lista de tuplas, cada una conteniendo
                                          un documento y su puntuacion de similitud.
        """
        logger.info("Iniciando busqueda de similitud para la consulta: '%s'", query[:50])
        query_embedding = self._generate_embedding(query)
        all_documents = self.document_repository.get_all()

        documents_with_embeddings = [doc for doc in all_documents if doc.embedding]
        if not documents_with_embeddings:
            logger.warning("No se encontraron documentos con embeddings para realizar la busqueda.")
            return []

        similarities = []
        for doc in documents_with_embeddings:
            similarity_score = self._cosine_similarity(query_embedding, doc.embedding)
            similarities.append((doc, similarity_score))

        similarities.sort(key=lambda item: item[1], reverse=True)
        
        logger.info("Busqueda completada. Devolviendo los %d resultados principales.", min(top_k, len(similarities)))
        return similarities[:top_k]