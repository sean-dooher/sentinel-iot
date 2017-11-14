
      var checkedIn = {"390439": false, "388483": false, "666": false}
      var idToPic = {"390439": "#sean", "388483": "#arjun", "666": "#victor"}
  

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

          case "666":
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






