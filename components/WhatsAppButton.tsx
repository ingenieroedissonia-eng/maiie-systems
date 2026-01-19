"use client";

export default function WhatsAppButton() {
  return (
    <a
      href="https://wa.me/573212053974?text=Hello%20I%20would%20like%20to%20discuss%20an%20AI%20opportunity"
      target="_blank"
      rel="noopener noreferrer"
      style={{
        position: "fixed",
        bottom: "16px",
        right: "16px",
        left: "16px", // 👈 permite buen comportamiento en móvil
        backgroundColor: "#25D366",
        color: "#ffffff",
        padding: "16px 20px",
        borderRadius: "999px",
        fontWeight: 600,
        textDecoration: "none",
        boxShadow: "0 8px 24px rgba(0,0,0,0.25)",
        zIndex: 9999,
        textAlign: "center",
        maxWidth: "480px", // 👈 se ve elegante en desktop
        marginLeft: "auto",
      }}
    >
      💬 Talk to an AI Systems Architect
    </a>
  );
}
