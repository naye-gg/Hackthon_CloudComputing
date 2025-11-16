const { put } = require("../../db/put");

/**
 * Handle WebSocket connection
 * Route: $connect
 */
exports.handler = async (event) => {
  try {
    const connectionId = event.requestContext.connectionId;

    // Store connection in DynamoDB
    await put("WebSocketConnections", {
      connectionId,
      conectadoEn: new Date().toISOString()
    });

    console.log(`Conexión establecida: ${connectionId}`);

    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Conectado" })
    };

  } catch (error) {
    console.error("Error en connect:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: "Error al conectar",
        error: error.message
      })
    };
  }
};
