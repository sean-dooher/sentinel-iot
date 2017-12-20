
      var checkedIn = {"390439": false, "388483": false, "407114": false, "389104": false}
      var idToPic = {"390439": "#sean", "388483": "#arjun", "407114": "#victor", "389104": "#adam"}
  

      function checkIn(studentId) {
        if (!checkedIn[studentId]) {
          playAudio(studentId, 1);
          revealFunc(idToPic[studentId]);
          checkedIn[studentId] = true;
        }
      }

      function checkOut(studentId) {
        if (checkedIn[studentId]) {
          playAudio(studentId, 0);
          hideFunc(idToPic[studentId]);
          checkedIn[studentId] = false;
        } 
      }

      function revealFunc(person) {
        var image = document.querySelector(person + " img");
        var badge = document.querySelector(person + " .badge");

        image.style.animation = "glow 1s infinite alternate";
        image.style.opacity = "1.0";
        image.style.filter = "none";

        $(person + " .badge").fadeOut(300, function() {
            badge.classList.remove("badge-warning");
            badge.classList.add("badge-success");
            badge.innerHTML = "At Home";
          })

        $(person + " .badge").fadeIn();
      }
 
      function hideFunc(person) {
        var image = document.querySelector(person + " img");
        var badge = document.querySelector(person + " .badge");
        
        image.style.animation = "";
        image.style.opacity = "0.5";
        image.style.filter = "grayscale(100%)";

        $(person + " .badge").fadeOut(300, function() {
            badge.classList.remove("badge-success");
            badge.classList.add("badge-warning");
            badge.innerHTML = "Away";
          })
        $(person + " .badge").fadeIn();
      }

      function playAudio(studentId, status) {
        switch(studentId) {
          case "390439":
            if (status == 1) {
              new Audio(samsung_flowers).play();
            } else if (status == 0) {
              new Audio(notification11).play();
            }
            break;

          case "388483":
            if (status == 1) {
              new Audio(samsung_flowers).play();
           } else if (status == 0) {
              new Audio(notification11).play();
            break;
          }

          case "407114":
            if (status == 1) {
              new Audio(samsung_flowers).play();
           } else if (status == 0) {
              new Audio(notification11).play();
            break;
          }

          case "389104":
            if (status == 1) {
              new Audio(samsung_flowers).play();
           } else if (status == 0) {
              new Audio(notification11).play();
            break;
          }

          default:
            break;
        }

      }

      var leaf1 = new Leaf("rfid_demo", "demo_website", "0ca89614-96fa-4d98-9ba2-c59fe044f407", "ws://" + window.location.host + "/hub/");
      leaf1.subscribe("0d51974f-90f1-4fec-af45-5bf319186304", rfidHandler);

      function rfidHandler(message) {
        console.log("bepopobpiduop");
        if (message.type === "DEVICE_STATUS") {
          var studentId = message.value.toString();
          if (studentId in checkedIn) {
            if (checkedIn[studentId]) {
              checkOut(studentId);     
            } else {
              checkIn(studentId);
            }
          }
        }
      }

      function startTimer(duration, display) {
        var timer = duration, minutes, seconds;
        var myVar = setInterval(function () {
            minutes = parseInt(timer / 60, 10)
            seconds = parseInt(timer % 60, 10);

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            display.textContent = minutes + ":" + seconds;

            if (--timer < 0) {
                deactivateBLM();
                myStopFunction(myVar);
            }
        }, 1000);
      }

      function myStopFunction(myVar) {
        clearInterval(myVar);
      }

    function activateBLM() {
      var fiveMinutes = 60 * 1, 
          timeText = document.querySelector('#time-text');
          timeText.style.display = "table-cell";
          document.getElementById("main").classList.add("blur");
          document.getElementById("time-overlay").style.display = "block";
          new Audio(blm_activated).play();

      startTimer(fiveMinutes, timeText);
    };

    function deactivateBLM() {
      document.querySelector('#time-text').style.display = "none";
      document.getElementById("time-overlay").style.display = "none";
      document.getElementById("main").classList.remove("blur");
      new Audio(blm_deactivated).play();
      myStopFunction();

    }


    // Smoothie Graph Random Data
    var line1 = new TimeSeries();
    var line2 = new TimeSeries();
    var line3 = new TimeSeries(); 

    // This is where to get live data
    function httpGet(theUrl, callBack)
	{
	    var xmlHttp = new XMLHttpRequest();
	    xmlHttp.open( "GET", theUrl, true ); // false for synchronous request
	    xmlHttp.onreadystatechange = function() {

	   	if (this.responseText && this.status == 200) {
	    		callBack(JSON.parse(this.responseText));
	    	}
	    }
	    xmlHttp.send( null );
	}


	

    setInterval(function() {
    	function get1(item) {
    		line1.append(new Date().getTime(), item.sellingQuantity);
    	}
    	function get2(item) {
    		line2.append(new Date().getTime(), item.sellingQuantity);
    	}
    	function get3(item) {
    		line3.append(new Date().getTime(), item.sellingQuantity);
    	}


    	httpGet("https://api.rsbuddy.com/grandExchange?a=guidePrice&i=560", get1);
    	httpGet("https://api.rsbuddy.com/grandExchange?a=guidePrice&i=565", get2);
    	httpGet("https://api.rsbuddy.com/grandExchange?a=guidePrice&i=561", get3);	

    }, 1000);

    var smoothie = new SmoothieChart({ grid: { strokeStyle: 'rgba(255, 255, 255, 0.2)', fillStyle: 'rgb(0, 30, 60)', lineWidth: 1, millisPerLine: 250, verticalSections: 6 } , minValue:200000,maxValue:500000});
    smoothie.addTimeSeries(line1, { strokeStyle: 'rgb(244, 241, 66)', fillStyle: 'rgba(244, 241, 66, 0.4)', lineWidth: 2 });
    smoothie.addTimeSeries(line2, { strokeStyle: 'rgb(0, 0, 212)', fillStyle: 'rgba(0, 0, 212, 0.4)', lineWidth: 2 });
    smoothie.addTimeSeries(line3, { strokeStyle: 'rgb(102, 22, 35)', fillStyle: 'rgba(102, 22, 35, 0.4)', lineWidth: 2 });
    smoothie.streamTo(document.getElementById("mycanvas"), 1000);



    router = new NetgearRouter("alwaysrises");
    router.login();
    router.getTrafficMeter().then((result) => {
		console.log(result);
	})









