const AWS = require("aws-sdk");
const dynamo = new AWS.DynamoDB.DocumentClient();

/**
 * Handle WebSocket disconnection
 * Route: $disconnect
 */
exports.handler = async (event) => {
  try {
    const connectionId = event.requestContext.connectionId;

    // Remove connection from DynamoDB
    await dynamo.delete({
      TableName: "WebSocketConnections",
      Key: { connectionId }
    }).promise();

    console.log(`Conexión cerrada: ${connectionId}`);

    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Desconectado" })
    };

  } catch (error) {
    console.error("Error en disconnect:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: "Error al desconectar",
        error: error.message
      })
    };
  }
};
