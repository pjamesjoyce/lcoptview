// This function creates a new node from external data
var newNodeExternal = function(name, type, id, x, y, ext_item_data, instance, outputlabel){
  
  if(outputlabel !== ''){instance.data.outputlabels[id] = outputlabel;}
  //console.log(outputlabel)
  //console.log(instance.data.outputlabels[id])
  //var id = id; //name.split(' ').join('_')//jsPlumbUtil.uuid();
  console.log(type)
  var d;
  if(type == 'input' || type == 'biosphere'){
    d = $('<div data-toggle="popover" data-trigger="hover" title="'+name+'" data-content="'+ext_item_data+'" data-html="true">').attr('id', id).addClass('w ' + type);  
  }else{
    d = $('<div>').attr('id', id).addClass('w ' + type);
  }
    
  var title =  $('<div>').addClass('title').text(name);

  d.append(title);

  var canvas = $("#sandbox_container");
  canvas.append(d);

  d.css('left', x + "px");
  d.css('top', y + "px");

  $('[data-toggle="popover"]').popover({
    container: '#sandbox_container',
    delay: {
       show: "100",
       hide: "100"
    },
  });

  return d;
};



var initNode = function(el, instance) {

            var i = instance;
            // initialise draggable elements.
            instance.draggable(el, {
              grid: [0.5,0.5],
              containment:true,
            });
};