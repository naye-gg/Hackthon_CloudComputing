const AWS = require("aws-sdk");
const dynamo = new AWS.DynamoDB.DocumentClient();

/**
 * Get item from DynamoDB table
 * @param {string} tableName - Name of the table
 * @param {object} key - Key object (e.g., { userId: "123" })
 */
async function get(tableName, key) {
  const params = {
    TableName: tableName,
    Key: key
  };

  const result = await dynamo.get(params).promise();
  return result.Item;
}

module.exports = { get };
