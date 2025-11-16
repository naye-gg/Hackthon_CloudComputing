const { v4 } = require("uuid");
const bcrypt = require("bcryptjs");
const { put } = require("../../db/put");
const { query } = require("../../db/query");

/**
 * Register a new user
 * POST /auth/register
 * Body: { email, password, rol }
 */
exports.handler = async (event) => {
  try {
    const data = JSON.parse(event.body);
    const { email, password, rol } = data;

    // Validate required fields
    if (!email || !password || !rol) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ok: false,
          message: "Email, password y rol son requeridos"
        })
      };
    }

    // Check if user already exists
    const existingUsers = await query("Usuarios", {
      IndexName: "EmailIndex",
      KeyConditionExpression: "email = :email",
      ExpressionAttributeValues: {
        ":email": email
      }
    });

    if (existingUsers && existingUsers.length > 0) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ok: false,
          message: "El email ya está registrado"
        })
      };
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const userId = "USR_" + v4().slice(0, 5);
    const newUser = {
      userId,
      email,
      password: hashedPassword,
      rol,
      fechaCreacion: new Date().toISOString()
    };

    await put("Usuarios", newUser);

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ok: true,
        userId,
        message: "Usuario registrado correctamente"
      })
    };

  } catch (error) {
    console.error("Error en register:", error);
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ok: false,
        message: "Error al registrar usuario",
        error: error.message
      })
    };
  }
};
