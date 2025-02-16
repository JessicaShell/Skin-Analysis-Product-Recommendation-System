const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');
const { Sequelize, DataTypes } = require('sequelize');

const app = express();
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static('uploads'));

// MySQL Connection
const sequelize = new Sequelize('skinDB', 'root', 'admin', {
    host: 'localhost',
    dialect: 'mysql'
});

sequelize.authenticate()
    .then(() => console.log('MySQL Connected'))
    .catch(err => console.log('Error:', err));

// Sequelize Model
const Analysis = sequelize.define('Analysis', {
    imagePath: DataTypes.STRING,
    skinTone: DataTypes.STRING,
    oiliness: DataTypes.STRING,
    redness: DataTypes.STRING,
    pimples: DataTypes.STRING,
    openPores:DataTypes.STRING,
    recommendations: DataTypes.TEXT
});

sequelize.sync();

// Multer Setup
const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, 'uploads/'),
    filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});
const upload = multer({ storage });

// API Endpoint
app.post('/api/analyze', upload.single('image'), async (req, res) => {
    try {
        const imagePath = req.file.path;
        const flaskResponse = await axios.post('http://localhost:5001/analyze', { imagePath });

         // Prepare skin issues for recommendation API
         const skinIssues = [
            flaskResponse.data.oiliness ? "oily" : "",
            flaskResponse.data.redness ? "redness" : "",
            flaskResponse.data.pimples ? "pimples" : "",
            flaskResponse.data.openPores ? "openPores" : ""
        ].filter(Boolean);

        // Send detected skin issues to Flask recommendation system
        const recResponse = await axios.post('http://localhost:5002/recommend', { skin_issues: skinIssues });

        const analysis = await Analysis.create({
            imagePath,
            skinTone: flaskResponse.data.skinTone,
            oiliness: flaskResponse.data.oiliness,
            redness: flaskResponse.data.redness,
            pimples: flaskResponse.data.pimples,
            openPores:flaskResponse.data.openPores,
            recommendations: JSON.stringify(recResponse.data.recommendations) // Store recommendations in DB
        });

        // Return results to frontend
        res.json({
            ...analysis.dataValues,
            recommendations: recResponse.data.recommendations // Send recommendations in response
        });
    } catch (error) {
        console.error(error);
        res.status(500).send('Server Error');
    }
});

app.listen(8000, () => console.log('Server running on port 8000'));
