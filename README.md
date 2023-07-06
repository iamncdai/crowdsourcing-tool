# Crowdsourcing Tool

## Install

Clone Source Code

```bash
git clone git@github.com:iamncdai/crowdsourcing-tool.git
cd crowdsourcing-tool
docker-compose up -d
```

Database Configuration
- Access: `http://localhost:8080`
- Login with Username/Password: `root/18120113`
- Create Dabatase: `crowdsourcing_tool`
- Import data from file: `crowdsourcing_tool.sql`

Congratulations on completing the Website installation, access http://localhost:4000/api to use.

## Features

### Auth
- Login: http://localhost:4000/api/auth/login
- Get Profile: http://localhost:4000/api/auth/me

## Libs
- Flask
- bcrypt
- PyJWT
- mysql-connector-python
