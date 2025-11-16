const AWS = require("aws-sdk");
const dynamo = new AWS.DynamoDB.DocumentClient();

/**
 * Send notification to WebSocket clients
 * Route: notify
 * Body: { type, incidenteId, estado, ... }
 */
exports.handler = async (event) => {
  try {
    const connectionId = event.requestContext.connectionId;
    const domain = event.requestContext.domainName;
    const stage = event.requestContext.stage;

    const apiGateway = new AWS.ApiGatewayManagementApi({
      endpoint: `${domain}/${stage}`
    });

    // Parse message
    const message = JSON.parse(event.body);

    // Get all connections
    const connections = await dynamo.scan({
      TableName: "WebSocketConnections"
    }).promise();

    console.log(`Enviando notificación a ${connections.Items.length} conexiones`);

    // Send message to all connections
    const sendPromises = connections.Items.map(async ({ connectionId: connId }) => {
      try {
        await apiGateway.postToConnection({
          ConnectionId: connId,
          Data: JSON.stringify(message)
        }).promise();
      } catch (error) {
        console.error(`Error enviando a ${connId}:`, error);

        // If connection is stale (410), remove it
        if (error.statusCode === 410) {
          await dynamo.delete({
            TableName: "WebSocketConnections",
            Key: { connectionId: connId }
          }).promise();
        }
      }
    });

    await Promise.all(sendPromises);

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: "Notificación enviada",
        sentTo: connections.Items.length
      })
    };

  } catch (error) {
    console.error("Error en notify:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: "Error al enviar notificación",
        error: error.message
      })
    };
  }
};
