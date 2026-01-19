"use client";

export default function WhatsAppButton() {
  return (
    <a
      href="https://wa.me/573212053974?text=Hello%2C%20I%20reviewed%20your%20MAIIE%20Systems%20platform.%20I%E2%80%99d%20like%20to%20discuss%20an%20AI%2FDecision%20Systems%20opportunity."
      target="_blank"
      rel="noopener noreferrer"
      style={{
        position: "fixed",
        bottom: "16px",
        right: "16px",
        left: "16px", // comportamiento correcto en móvil
        backgroundColor: "#25D366",
        color: "#ffffff",
        padding: "16px 20px",
        borderRadius: "999px",
        fontWeight: 600,
        textDecoration: "none",
        boxShadow: "0 8px 24px rgba(0,0,0,0.25)",
        zIndex: 9999,
        textAlign: "center",
        maxWidth: "480px", // elegante en desktop
        marginLeft: "auto",
        marginRight: "auto",
      }}
    >
      💬 Talk to an AI Systems Architect
    </a>
  );
}
