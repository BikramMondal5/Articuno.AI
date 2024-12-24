const express = require('express');
const app = express();

// Serve static files from the "public" directory
app.use(express.static('public'));


// Start the server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
