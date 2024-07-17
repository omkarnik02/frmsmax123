const inputs = document.querySelectorAll(".input");
function addcl(){
	let parent = this.parentNode.parentNode;
	parent.classList.add("focus");
}

function remcl(){
	let parent = this.parentNode.parentNode;
	if(this.value == ""){
		parent.classList.remove("focus");
	}
}
inputs.forEach(input => {
	input.addEventListener("focus", addcl);
	input.addEventListener("blur", remcl);
});

function toggleContent() {
    var content = document.getElementById("filter");
    if (content.style.display === "none") {
      content.style.display = "block";
    } else {
      content.style.display = "none";
    }
  }

//navbar active link
document.addEventListener('DOMContentLoaded', function() {
	// Get current path or URL
	var currentPath = window.location.pathname;

	// Get all navbar items
	var navbarItems = document.querySelectorAll('.navbar .item');

	// Add 'active' class to the current navbar item based on conditions
	navbarItems.forEach(function(item) {
		var link = item.querySelector('.navbar-a');
		var href = link.getAttribute('href');
		if (currentPath.startsWith(href)) {
			item.classList.add('active');
		}
	});
});
// active link end

// rules html 

//rules end

