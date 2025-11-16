const AWS = require("aws-sdk");
const dynamo = new AWS.DynamoDB.DocumentClient();

/**
 * Query items from DynamoDB table
 * @param {string} tableName - Name of the table
 * @param {object} options - Query options
 */
async function query(tableName, options = {}) {
  const params = {
    TableName: tableName,
    ...options
  };

  const result = await dynamo.query(params).promise();
  return result.Items;
}

/**
 * Scan all items from DynamoDB table
 * @param {string} tableName - Name of the table
 */
async function scan(tableName) {
  const params = {
    TableName: tableName
  };

  const result = await dynamo.scan(params).promise();
  return result.Items;
}

module.exports = { query, scan };
