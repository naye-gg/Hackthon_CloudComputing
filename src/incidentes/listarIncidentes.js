const { scan } = require("../../db/query");

/**
 * List all incidents
 * GET /incidentes
 */
exports.handler = async (event) => {
  try {
    const incidentes = await scan("Incidentes");

    // Sort by creation date (newest first)
    const sortedIncidentes = incidentes.sort((a, b) => {
      return new Date(b.fechaCreacion) - new Date(a.fechaCreacion);
    });

    // Format response
    const items = sortedIncidentes.map(inc => ({
      incidenteId: inc.incidenteId,
      tipo: inc.tipo,
      estado: inc.estado,
      ubicacion: inc.ubicacion,
      urgencia: inc.urgencia,
      descripcion: inc.descripcion,
      fechaCreacion: inc.fechaCreacion
    }));

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ok: true,
        items
      })
    };

  } catch (error) {
    console.error("Error en listarIncidentes:", error);
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ok: false,
        message: "Error al listar incidentes",
        error: error.message
      })
    };
  }
};
