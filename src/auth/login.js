const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const { query } = require("../../db/query");

const JWT_SECRET = process.env.JWT_SECRET || "utec-secret-key-2025";

/**
 * Login user
 * POST /auth/login
 * Body: { email, password }
 */
exports.handler = async (event) => {
  try {
    const data = JSON.parse(event.body);
    const { email, password } = data;

    // Validate required fields
    if (!email || !password) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ok: false,
          message: "Email y password son requeridos"
        })
      };
    }

    // Find user by email
    const users = await query("Usuarios", {
      IndexName: "EmailIndex",
      KeyConditionExpression: "email = :email",
      ExpressionAttributeValues: {
        ":email": email
      }
    });

    if (!users || users.length === 0) {
      return {
        statusCode: 401,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ok: false,
          message: "Credenciales inválidas"
        })
      };
    }

    const user = users[0];

    // Verify password
    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      return {
        statusCode: 401,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ok: false,
          message: "Credenciales inválidas"
        })
      };
    }

    // Generate JWT token
    const token = jwt.sign(
      {
        userId: user.userId,
        email: user.email,
        rol: user.rol
      },
      JWT_SECRET,
      { expiresIn: "24h" }
    );

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ok: true,
        token,
        user: {
          userId: user.userId,
          rol: user.rol
        }
      })
    };

  } catch (error) {
    console.error("Error en login:", error);
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ok: false,
        message: "Error al iniciar sesión",
        error: error.message
      })
    };
  }
};
