const { get } = require("../../db/get");

/**
 * Get a specific incident by ID
 * GET /incidentes/{id}
 */
exports.handler = async (event) => {
  try {
    const incidenteId = event.pathParameters.id;

    if (!incidenteId) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ok: false,
          message: "ID de incidente requerido"
        })
      };
    }

    const incidente = await get("Incidentes", { incidenteId });

    if (!incidente) {
      return {
        statusCode: 404,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ok: false,
          message: "Incidente no encontrado"
        })
      };
    }

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ok: true,
        incidente
      })
    };

  } catch (error) {
    console.error("Error en obtenerIncidente:", error);
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ok: false,
        message: "Error al obtener incidente",
        error: error.message
      })
    };
  }
};
