const AWS = require("aws-sdk");
const dynamo = new AWS.DynamoDB.DocumentClient();

/**
 * Update item in DynamoDB table
 * @param {string} tableName - Name of the table
 * @param {object} key - Key object
 * @param {string} updateExpression - Update expression
 * @param {object} expressionAttributeValues - Values for the expression
 * @param {object} expressionAttributeNames - Names for the expression (optional)
 */
async function update(tableName, key, updateExpression, expressionAttributeValues, expressionAttributeNames = null) {
  const params = {
    TableName: tableName,
    Key: key,
    UpdateExpression: updateExpression,
    ExpressionAttributeValues: expressionAttributeValues,
    ReturnValues: "ALL_NEW"
  };

  if (expressionAttributeNames) {
    params.ExpressionAttributeNames = expressionAttributeNames;
  }

  const result = await dynamo.update(params).promise();
  return result.Attributes;
}

module.exports = { update };
