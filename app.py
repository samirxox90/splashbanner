<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Website Under Maintenance</title>
  <style>
    /* Reset */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: radial-gradient(circle at top, #4b0082, #000);
      color: #fff;
    }

    /* Animated background stars */
    .stars {
      width: 2px;
      height: 2px;
      background: white;
      box-shadow: 
        50px 80px white, 150px 120px white, 250px 200px white, 
        350px 50px white, 450px 150px white, 550px 250px white,
        650px 300px white, 750px 100px white, 850px 400px white,
        950px 200px white;
      animation: twinkle 5s infinite alternate;
    }

    @keyframes twinkle {
      from { opacity: 0.2; }
      to { opacity: 1; }
    }

    /* Maintenance text */
    .message {
      text-align: center;
      position: absolute;
      z-index: 2;
    }

    .message h1 {
      font-size: 3em;
      color: #fff;
      text-shadow: 0 0 15px #9d4edd, 0 0 25px #c77dff;
      animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
      from {
        text-shadow: 0 0 10px #9d4edd, 0 0 20px #c77dff;
      }
      to {
        text-shadow: 0 0 20px #c77dff, 0 0 40px #e0aaff;
      }
    }

    .message p {
      margin-top: 15px;
      font-size: 1.2em;
      color: #ddd;
    }

    /* Floating nebula effect */
    .nebula {
      position: absolute;
      width: 600px;
      height: 600px;
      background: radial-gradient(circle, rgba(157, 77, 237, 0.5), transparent 70%);
      border-radius: 50%;
      animation: float 15s infinite alternate ease-in-out;
      filter: blur(150px);
    }

    .nebula:nth-child(2) {
      width: 400px;
      height: 400px;
      left: 70%;
      top: 20%;
      animation-duration: 20s;
    }

    @keyframes float {
      from { transform: translateY(0px) translateX(0px); }
      to { transform: translateY(-50px) translateX(50px); }
    }

  </style>
</head>
<body>
  <div class="stars"></div>
  <div class="nebula"></div>
  <div class="nebula"></div>
  
  <div class="message">
    <h1> Website Under Maintenance </h1>
    <p>We’ll be back soon with something amazing!</p>
  </div>
</body>
</html>
