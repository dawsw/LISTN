document.addEventListener("DOMContentLoaded", function() {
  const squares = document.getElementsByClassName('playlistsquare');
  for (let i = 0; i < squares.length; i++) {
      const square = squares[i];

      square.addEventListener("mouseover", function() {
        // Change background color on mouseover
        square.style.backgroundColor = lightenColor(color);
    });

      square.addEventListener("mouseout", function() {
        // Restore original background color on mouseout
        square.style.backgroundColor = color; // Or whatever the original color was
    });
    
      const color = generateRandomColor();
      square.style.backgroundColor = color;
  }
});

function lightenColor(color) {
  // Extract the RGB values
  let rgb = color.match(/\d+/g);
  let r = parseInt(rgb[0]);
  let g = parseInt(rgb[1]);
  let b = parseInt(rgb[2]);

  // Increase the brightness by a certain factor (e.g., 1.3)
  r = Math.min(Math.floor(r * 1.4), 255);
  g = Math.min(Math.floor(g * 1.4), 255);
  b = Math.min(Math.floor(b * 1.4), 255);

  // Construct the new color string
  return `rgb(${r}, ${g}, ${b})`;
}


function generateRandomColor() {
  const r = Math.floor((Math.random() * 256) * 0.7);
  const g = Math.floor((Math.random() * 256) * 0.7);
  const b = Math.floor((Math.random() * 256) * 0.8);
  return `rgb(${r}, ${g}, ${b})`;
}



function wishlistButton (event) {
  var scorebox = document.getElementById('score');
  scorebox.removeAttribute('required');

}

function togglePlayPause(index) {
  var audioPlayer = document.getElementById('audioPlayer' + index);
  var playPauseImage = document.getElementById('playpauseimage' + index);
  var volumeSlider = document.getElementById('volumeSlider' + index);
  audioPlayer.volume = .3;
  
  if (audioPlayer.paused) {
      audioPlayer.volume = .3;
      audioPlayer.play();
      playPauseImage.src = 'static/images/pausebutton.png';
      volumeSlider.removeAttribute('hidden');
  } else {
      audioPlayer.pause();
      playPauseImage.src = 'static/images/playbutton1.png';
      volumeSlider.setAttribute('hidden', true);
  }
}

function setVolume(index) {
  var audio = document.getElementById('audioPlayer' + index);
  var volumeSlider = document.getElementById('volumeSlider' + index);
  audio.volume = volumeSlider.value / 100;
}


document.addEventListener("DOMContentLoaded", function() {
  // Function to add horizontal scroll behavior to an element
  function addHorizontalScrollBehavior(elementId) {
    const container = document.getElementById(elementId);

    container.addEventListener("wheel", function(event) {
      // Check if the event is horizontal scroll
      if (event.deltaX !== 0) {
        container.scrollLeft += event.deltaX;
      } else if (event.deltaY !== 0) { // For browsers that don't support deltaX
        container.scrollLeft += event.deltaY * 1; // Adjust the speed as needed
      }
    });
  }

  // Call the function for each element you want to add the behavior to
  addHorizontalScrollBehavior("homepage_newreleases");
  addHorizontalScrollBehavior("homepage_topmusic");
  // Add more calls if needed for other elements
});

function refreshPage() {
  location.reload(); // Reloads the current page
}


// edit button for album_details page
document.addEventListener('DOMContentLoaded', function() {
  var editButton = document.getElementById('editbutton');
  var deleteButton = document.getElementById('deletebutton');
  var submitButton = document.getElementById('submitbutton');
  var commentsTextarea = document.querySelector('.commentbox');
  var scoreContainer = document.getElementById('editscore');

  editButton.addEventListener('click', function(event) {
      // Prevent default form submission behavior
      event.preventDefault();

      // Remove readonly attribute from the textarea
      commentsTextarea.removeAttribute('readonly');

      editButton.parentNode.removeChild(editButton);

      // create save changes button
      var editbutton = document.createElement('button');
      editbutton.setAttribute('type', 'submit');
      editbutton.setAttribute('class', 'submit_score');
      editbutton.setAttribute('id', 'editscore');
      editbutton.textContent = 'Save Changes';
      deleteButton.parentNode.appendChild(editbutton);

      // create discard changes
      var discardbutton = document.createElement('button');
      discardbutton.setAttribute('type', 'button');
      discardbutton.setAttribute('style', 'margin-left: 5%')
      discardbutton.setAttribute('class', 'submit_score');
      discardbutton.setAttribute('id', 'discardscore');
      discardbutton.setAttribute('onclick', 'refreshPage()')
      discardbutton.textContent = 'Discard Changes';
      deleteButton.parentNode.appendChild(discardbutton);
    
      
      // Remove delete button
      deleteButton.parentNode.removeChild(deleteButton);

      var inputElement = document.createElement('input');
        inputElement.setAttribute('class', 'scoreinput');
        inputElement.setAttribute('placeholder', scoreContainer.textContent);
        inputElement.setAttribute('name', 'score');
        inputElement.setAttribute('type', 'number');
        inputElement.setAttribute('min', '0');
        inputElement.setAttribute('max', '100');
        inputElement.setAttribute('autocomplete', 'off');
        inputElement.setAttribute('required', 'required');
        inputElement.setAttribute('autofocus', 'autofocus');

        // Replace the existing span with the new input element
        scoreContainer.parentNode.replaceChild(inputElement, scoreContainer);

  });
});

// change LISTN Score color
function updateListnScoreColor() {
  // Get all elements with the class 'recent_rating_number'
  const recentRatingNumbers = document.getElementsByClassName('recent_rating_number');

  // Loop through each element
  for (let i = 0; i < recentRatingNumbers.length; i++) {
    const recentRatingNumber = recentRatingNumbers[i];
    const listnScore = document.getElementById('listn_score'); // Assuming your listn_score IDs are also indexed

    // Get the values as integers
    const value = parseInt(listnScore.textContent);
    const recentRatingValue = parseInt(recentRatingNumber.textContent);

    // Update styles based on the values
    if (!isNaN(value)) {
      if (value >= 85 && value < 101) {
        listnScore.style.color = "rgb(57, 250, 121)";     
      } else if(value >= 70 && value < 85) {
        listnScore.style.color = "rgb(171, 255, 183)";
      } else if (value >= 45 && value < 70) {
        listnScore.style.color = "rgb(230, 255, 171)";
      } else if (value >= 30 && value < 45) {
        listnScore.style.color = "rgb(250, 151, 151)";
      } else if (value >= 0 && value < 30) {
        listnScore.style.color = "rgb(255, 86, 86)";
      }
    }

    if (!isNaN(recentRatingValue)) {
      if (recentRatingValue >= 85 && recentRatingValue < 101) {
        recentRatingNumber.style.color = "rgb(57, 250, 121)";     
      } else if(recentRatingValue >= 70 && recentRatingValue < 85) {
        recentRatingNumber.style.color = "rgb(171, 255, 183)";
      } else if (recentRatingValue >= 45 && recentRatingValue < 70) {
        recentRatingNumber.style.color = "rgb(230, 255, 171)";
      } else if (recentRatingValue >= 30 && recentRatingValue < 45) {
        recentRatingNumber.style.color = "rgb(250, 151, 151)";
      } else if (recentRatingValue >= 0 && recentRatingValue < 30) {
        recentRatingNumber.style.color = "rgb(255, 86, 86)";
      }
    }
  }
}

// Call the function
updateListnScoreColor();


function insertLoginInput() {

  //get all information from page
  const backarrow = document.getElementById('backarrow');
  const loginbutton = document.getElementById('login');
  const message = document.getElementById('message');
  const infocontainer = document.querySelector('.container');
  var form = document.createElement('form');
  var username = document.createElement('input');
  const div = document.createElement('div');
  const div2 = document.createElement('div');
  var password = document.createElement('input');
  const button = document.createElement('input');

  //remove any existing error messages
  if (message) {
    message.remove();
  }

  //show back arrow
  backarrow.classList.remove('hidden');

  //get form method and action
  form.action = '/';
  form.method = 'post';

  //define username details
  username.name = 'username'
  username.type = 'text';
  username.placeholder = 'Username';
  username.className = 'loginform';
  username.autocomplete = 'off';
  username.required = true;

  //define div classes
  div.className = 'logindiv';
  div2.className = 'logindiv';

  //define password details
  password.name = 'password'
  password.type = 'password';
  password.placeholder = 'Password';
  password.className = 'loginform';
  password.required = true;
  password.title = 'Password must be at least 8 characters long and contain';

  //define button details
  button.type = 'submit'
  button.className = 'loginbutton'
  button.value = 'login'
  
  //append all to form 
  form.appendChild(username); 
  form.appendChild(div);
  form.appendChild(password);
  form.appendChild(div2);
  form.appendChild(button);

  // Append form to the container
  infocontainer.appendChild(form); 
  
}


function insertRegisterInput() {

  //get all information from page
  const backarrow = document.getElementById('backarrow');
  const registerbutton = document.getElementById('register');
  const message = document.getElementById('message');
  const infocontainer = document.querySelector('.container');
  var form = document.createElement('form');
  var username = document.createElement('input');
  const div = document.createElement('div');
  const div2 = document.createElement('div');
  const div3 = document.createElement('div');
  var password = document.createElement('input');
  var confirm_password = document.createElement('input');
  const button = document.createElement('input');
  const errorElement = document.createElement('div');

  //remove any existing error messages
  if (message) {
    message.remove();
  }

  //show back arrow
  backarrow.classList.remove('hidden');
  
  //get form method and action
  form.action = '/';
  form.method = 'post';
  form.id = 'form';

  //define username details
  username.name = 'username';
  username.type = 'text';
  username.maxLength = 12;
  username.minLength = 5;
  username.placeholder = 'Choose a Username';
  username.className = 'loginform';
  username.required = true;
  username.autocomplete = 'off';
  username.pattern = '[a-zA-Z0-9]{6, }'
  username.title = 'Must be at least 5 characters'


  //define div classes
  div.className = 'logindiv';
  div2.className = 'logindiv';
  div3.className = 'logindiv';

  //define password details
  password.name = 'password';
  password.id = 'password';
  password.type = 'password';
  password.minLength = 8;
  password.placeholder = 'Enter Password';
  password.className = 'loginform';
  password.required = true;
  password.title = 'Must enter password';

  //define confirm password details
  confirm_password.name = 'confirm_password';
  confirm_password.id = 'confirm_password'; 
  confirm_password.type = 'password';
  confirm_password.placeholder = 'Confirm Password';
  confirm_password.className = 'loginform';
  confirm_password.required = true;

  //define button details
  button.type = 'submit';
  button.className = 'loginbutton';
  button.value = 'login';

  //define error div
  errorElement.id = 'error';
  
  //append all to form 
  form.appendChild(errorElement);
  form.appendChild(username);
  form.appendChild(div);
  form.appendChild(password);
  form.appendChild(div2);
  form.appendChild(confirm_password);
  form.appendChild(div3);
  form.appendChild(button);

  // Append form to the container
  infocontainer.appendChild(form); 
  
}


function validateForm() {
  var searchbar = document.getElementById('searchbar').value.trim();
  if (searchbar === '') {
      return false;
  }
  return true;
}



function buttonclick(clickedButton) {
    // Get a reference to the button elements and description
    const buttons = document.querySelectorAll('[name="login"], [name="register"]');
    const description = document.querySelector('.login_description');
    const square = document.querySelector('.homesquare');
    const logo = document.querySelector('.logo');
    const bgvideo = document.querySelector('video-container')

    // Toggle the display of buttons and description
    buttons.forEach(button => {
        button.style.display = 'none';
    });

    description.style.display = 'none';

    // Get current square height
    const currentSquareHeight = square.getBoundingClientRect().height;

    //Move logo upwards and display forms
    if (clickedButton.getAttribute('name') == 'login') {
      const logocurrentTop = parseInt(getComputedStyle(logo).top);
      const logonewTop = logocurrentTop - 15;

      //change square height
      const newSquareHeight = currentSquareHeight + 200;
      square.style.height = `${newSquareHeight}px`;

      insertLoginInput();

      logo.style.top = `${logonewTop}px`;


    } else if (clickedButton.getAttribute('name') == 'register') {
      const logocurrentTop = parseInt(getComputedStyle(logo).top);
      const logonewTop = logocurrentTop - 10;
      logo.style.top = `${logonewTop}px`;

      //change square height
      const newSquareHeight = currentSquareHeight + 300;
      square.style.height = `${newSquareHeight}px`;
      
      insertRegisterInput();
    }

    //Shrink logo
    const currentLogoWidth = logo.clientWidth;
    const currentLogoHeight = logo.clientHeight;
    
    const newLogoWidth = currentLogoWidth * .75;
    const newLogoHeight = currentLogoHeight * .75;

    logo.style.width = `${newLogoWidth}px`;
    logo.style.height = `${newLogoHeight}px`;

  }

  const expandButtons = document.querySelectorAll('Button');
  expandButtons.forEach(button => {
      button.addEventListener('click', buttonclick);

});



