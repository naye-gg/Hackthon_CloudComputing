const { v4 } = require("uuid");
const { put } = require("../../db/put");

/**
 * Create a new incident
 * POST /incidentes
 * Body: { tipo, descripcion, ubicacion, urgencia }
 */
exports.handler = async (event) => {
  try {
    const data = JSON.parse(event.body);
    const { tipo, descripcion, ubicacion, urgencia } = data;

    // Validate required fields
    if (!tipo || !descripcion || !ubicacion || !urgencia) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ok: false,
          message: "Tipo, descripcion, ubicacion y urgencia son requeridos"
        })
      };
    }

    // Create incident
    const incidenteId = "INC_" + v4().slice(0, 6);

    const item = {
      incidenteId,
      tipo,
      descripcion,
      ubicacion,
      urgencia,
      estado: "pendiente",
      fechaCreacion: new Date().toISOString(),
      historial: [
        {
          accion: "creado",
          fecha: new Date().toISOString()
        }
      ]
    };

    await put("Incidentes", item);

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ok: true,
        incidenteId,
        estado: "pendiente"
      })
    };

  } catch (error) {
    console.error("Error en crearIncidente:", error);
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ok: false,
        message: "Error al crear incidente",
        error: error.message
      })
    };
  }
};
