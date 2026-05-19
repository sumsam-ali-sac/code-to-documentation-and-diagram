const express = require('express');
const app = express();
const port = 3000;

class UserService {
    constructor() {
        this.users = [];
    }

    addUser(user) {
        this.users.push(user);
    }
}

class User {
    constructor(name, email) {
        this.name = name;
        this.email = email;
    }
}

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
