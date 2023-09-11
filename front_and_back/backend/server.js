const jwt = require("jsonwebtoken")
const express = require('express');
const axios = require('axios');
const cors = require('cors')
const app = express();
const bodyParser = require('body-parser');

//use the proper flask root for pc:
const flask_root = "http://127.0.0.1:5000"
//const flast_root = "http://192.168.0.106:5000"

app.use(bodyParser.json());
app.use(cors());

app.get('/getcities', async (req, res) => {
  try {
    const response = await axios.get(flask_root+"/cities");
    console.log("getting cities");
    const cities = response.data;

    res.json(cities);
  } catch (error) {
    res.status(500).json({ error: 'Unable to fetch city data' });
  }
});

app.post('/add', async function (req, res) {
  console.log("add on post")
  
  data = JSON.parse(req.body.data);
  var options = {
    method: 'POST',
    url: flask_root+'/adduser',
    data: data,
    headers: {
      'Content-Type': 'application/json'
    }
  };
  try {
    const response = await axios(options);
    res.json(response.data)
  } catch (error) {
    console.log("error add user",error);
    res.json("failed to register user");
  }
});


app.post("/login", async (req, res) => {
  try {
    console.log("login");
    const response = await axios.post(flask_root+'/login');
    
    const sample_users = response.data;

    const data = JSON.parse(req.body.data);
    const email = data.email;
    const password = data.pwd;

    const user = sample_users.find(user =>
      user.email === email && user.password === password
    );

    if (user) {
      // Fetch additional user details from Neo4j
      const userDetails = await fetchUserDetailsFromNeo4j(user.usernum);
      if (userDetails) { 
        // Update user object with details from Neo4j
        user.name = userDetails.name;
        console.log(user.name)
        user.surname = userDetails.surname;
        user.gender = userDetails.gender;
        user.date_of_birth = userDetails.date_of_birth;
        user.city = userDetails.city;
        user.hobby = userDetails.hobby;
        
        // Send the updated user object in the response
        res.send(generateTokenResponse(user));
        console.log("user exists");
      } else {
        console.log("user details not found in Neo4j");
        res.status(400).send("User details not found.");
      }
    } else {
      console.log("user not found");
      res.status(400).send("Username or password is not correct.");
    }
  } catch (error) {
    console.error("Error processing login request:", error);
    res.status(500).json("Failed to process login request");
  }
});

//update user
app.post('/profile',async function(req,res){
  console.log("running update details (/profile)")
data = JSON.parse(req.body.data);
var options = {
  method: 'POST',
  url: flask_root+'/updateuser',
  data: data,
  headers: {
    'Content-Type': 'application/json'
  }
};
console.log(data)
try {
  const response = await axios(options);
  console.log(data)
  console.log("result " + response.data);
  res.json(response.data)
} catch (error) {
  console.log("error in update",error);
  res.json("failed to update user")
}
})

async function fetchUserDetailsFromNeo4j(usernum) {
  try {
      const response = await axios.get(flask_root+`/user/${usernum}`);
      console.log("response.data: ", response.data)
      return response.data;
  } catch (error) {
      console.error("error fetchUserDetailsFromNeo",error);
      return null;
  }
}

app.get('/fetchUserDetails/:usernum', async (req, res) => {
  const usernum = parseInt(req.params.usernum);
  try {
    const userDetails = await fetchUserDetails(usernum); // got user here with data from sql and neo4j
    console.log("user details:", userDetails);
    res.send(userDetails);
  } catch (error) {
    console.error("Error getting user info:", error);
    res.status(500).json({ error: "Error getting user info" });
  }
});

async function fetchUserDetails(usernum) {
  try {
      const responseNeo = await axios.get(flask_root+`/user/${usernum}`);
      console.log("response.data: ", responseNeo.data)
      const responseSql = await axios.get(flask_root+`/fetchUserDetailsFromSSQL/${usernum}`);
      console.log("response.data: ", responseSql.data)
      console.log(responseNeo)
      console.log(responseSql)
      const user ={};
      user.name = responseNeo.data.name
      user.surname = responseNeo.data.surname;
      user.gender = responseNeo.data.gender;
      user.date_of_birth = responseNeo.data.date_of_birth;
      user.city = responseNeo.data.city;
      user.hobby = responseNeo.data.hobby;
      user.password = responseSql.data.password;
      user.email = responseSql.data.email;
      user.usernum = responseSql.data.usernum;
      console.log("fetchUserDetails ----- user:", user)
      return user;
  } catch (error) {
      console.error(error);
      return null;
  }
}

const generateTokenResponse = (user)=>{
    const token = jwt.sign(
        {email:user.email, isAdmin:user.isAdmin}, "File", {expiresIn:"30d"});
    user.token = token;
    console.log(user)
    return user;
}

app.get('/:current_user_num', async (req, res) => {
  const current_user_num = parseInt(req.params.current_user_num);
  try {
    const response = await axios.get(flask_root+`/user/${current_user_num}`);
    const curUser = response.data;
    console.log("user is:", curUser);
    res.send(curUser);
  } catch (error) {
    console.error("Error getting user info:", error);
    res.status(500).json({ error: "Error getting user info" });
  }
});

app.get('/api/fetch_cluster_users/:current_user_num', async (req, res) => {
  const current_user_num = parseInt(req.params.current_user_num);
  try {
    const response = await axios.get(flask_root+`/clusterusers/${current_user_num}`);
    const clusterUsers = response.data;
    res.json(clusterUsers);
  } catch (error) {
    console.error("Error fetching cluster users:", error);
    res.status(500).json({ error: "Failed to fetch cluster users" });
  }
});


app.get('/api/fetch_all_users/:current_user_num', async (req, res) => {
  const current_user_num = parseInt(req.params.current_user_num);
  try {
    const response = await axios.get(flask_root+`/fetch_all_users/${current_user_num}`);
    const allUsers = response.data;
    res.json(allUsers);
  } catch (error) {
    console.error("Error fetching all users:", error);
    res.status(500).json({ error: "Failed to fetch all users" });
  }
});

app.get('/api/searchByExactHobby/:usernum/:queryStr', async (req, res) => {
  const usernum = parseInt(req.params.usernum);
  const queryStr = req.params.queryStr;
  console.log(queryStr)
  console.log(usernum)
    try {
      const response = await axios.get(flask_root+`/searchByExactHobby/${usernum}/${queryStr}`);
      const allUsers = response.data;
      if (allUsers.length==0){
        console.log("empty")
      }
      else{
        console.log("not empty")
      }
      res.json(allUsers);

  } catch (error) {
    console.error("Error searchByExactHobby:", error);
    res.status(500).json({ error: "Failed to searchByExactHobby" });
  }
});

app.get('/api/searchByOrHobby/:usernum/:queryStr', async (req, res) => {
  const usernum = parseInt(req.params.usernum);
  const queryStr = req.params.queryStr;
  console.log(queryStr)
  console.log(usernum)
    try {
      const response = await axios.get(flask_root+`/searchByOrHobby/${usernum}/${queryStr}`);
      const allUsers = response.data;
      if (allUsers.length==0){
        console.log("empty")
      }
      else{
        console.log("not empty")
      }
      res.json(allUsers);

  } catch (error) {
    console.error("Error searchByOrHobby:", error);
    res.status(500).json({ error: "Failed to searchByOrHobby" });
  }
});


//get all friends
app.get('/api/getFriends/:user_num', async (req, res) => {
  const user_num = parseInt(req.params.user_num);
  try {
    const response = await axios.get(flask_root+`/getFriends/${user_num}`);
    const users = response.data;
    res.json(users);
  } catch (error) {
    console.error("Error fetching friends:", error);
    res.status(500).json({ error: "Failed to fetch friends" });
  }
});

//add friends
app.get('/api/addFriend/:user_num/:friend_num', async (req, res) => {
  const user_num = parseInt(req.params.user_num);
  const friend_num = parseInt(req.params.friend_num);
  try {
    const response = await axios.get(flask_root+`/addFriend/${user_num}/${friend_num}`);
    res.json(response.data);
  } catch (error) {
    console.error("Error adding friend:", error);
    res.status(500).json({ error: "Failed to add friend" });
  }
});

//remove friends
app.get('/api/removeFriend/:user_num/:friend_num', async (req, res) => {
  const user_num = parseInt(req.params.user_num);
  const friend_num = parseInt(req.params.friend_num);
  try {
    const response = await axios.get(flask_root+`/removeFriend/${user_num}/${friend_num}`);
    res.json(response.data);
  } catch (error) {
    console.error("Error removing friend:", error);
    res.status(500).json({ error: "Failed to remove friend" });
  }
});

//check friend
app.get('/api/checkFriend/:user_num/:friend_num', async (req, res) => {
  const user_num = parseInt(req.params.user_num);
  const friend_num = parseInt(req.params.friend_num);
  try {
    const response = await axios.get(flask_root+`/checkFriend/${user_num}/${friend_num}`);
    res.json(response.data);
  } catch (error) {
    console.error("Error checking friend:", error);
    res.status(500).json({ error: "Failed to check friend" });
  }
});


//using google distance api
app.get('/api/distance/:city1/:city2', async (req, res) => {
  const city1=req.params.city1;
  const city2=req.params.city2;
  // Google Distance Matrix API key
  const apiKey = 'AIzaSyBB-NpJB1ceeWe1JkLHTDZBs2ujkg0Q_s0';
  try {
    // Make a request to the Google Distance Matrix API
    const response = await axios.get('https://maps.googleapis.com/maps/api/distancematrix/json', {
      params: {
        origins: city1+", UK",
        destinations: city2+", UK",
        key: apiKey,
      },
    });
    // Extract the distance from the API response
    const distance_text = response.data.rows[0].elements[0].distance.text;
    distance = parseFloat(distance_text.split(" ")[0]);
    res.json({ distance });
  } catch (error) {
    console.error('Error fetching distance from Google API:', error.message);
    res.status(500).json({ error: 'Unable to fetch distance from Google API' });
  }
});

app.listen(8080, () => {
    console.log('Listening on port 8080...');
;})

