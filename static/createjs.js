var id = 0;
var newinput = function() {
  var parent = document.getElementById(body_img_div)
  var field = document.createElement("input")
  field.className = "myclassname"
  field.type = "file"
  field.style = "display:block;"
  field.id = "input" + id;
  parent.appendChild(field);
  id += 1;
}
