const AWS = require("aws-sdk");
const dynamo = new AWS.DynamoDB.DocumentClient();

/**
 * Put item in DynamoDB table
 * @param {string} tableName - Name of the table
 * @param {object} item - Item to put
 */
async function put(tableName, item) {
  const params = {
    TableName: tableName,
    Item: item
  };

  return await dynamo.put(params).promise();
}

module.exports = { put };
