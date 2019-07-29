
var next="";
var cant=0;
var total=0;
var elements=[];
var flag=false;

//$("#tabla").hide();

load_posts("/api/v1/denuncias/");


function convert_to_readable_date(date_time_string) {
    var newDate = moment(date_time_string).format('DD/MM/YYYY, h:mm:ss a');
    return newDate;
}
// Load all posts on page load
function hideDivs () {
    if(flag){
        $("#vis").html("Ver como  galeria");
        $("#denuncias").hide();
        $("#tabla").show();
        
    }else{
        $("#vis").html("Ver como lista");
        $("#denuncias").show();
        $("#tabla").hide();
    }
    flag=!flag;

    // body...
}

function toTable(){
    var par="";
    //$("#denuncias").toggle();
    $("#tb").html("");
      for (var i = 0; i < elements.length; i++) {
        var par = ( i & 1 ) ? "pure-table-odd" : "";
        var desc = ( elements[i].desc ) ? elements[i].desc : "";
        var dateString = convert_to_readable_date(elements[i].added);
        $("#tb").append("<tr class='"+par+"' ><td>"+(i+1)+"</td><td><a href='/buscar/"+elements[i].numero + 
            "'>" + elements[i].numero+"</a> </td><td> "+elements[i].tipo+" </td> <td> " + desc + 
            " </td><td><a href='"+elements[i].screenshot +
            "' target='_blank'><i class='fa fa-file-image-o negro fa-lg' alt='icono foto' ></i> </a></td><td>" +
            dateString + " </tr>");
      }
}

function load_posts(url) {
    $.ajax({
        url : url, // the endpoint
        type : "GET", // http method
        // handle a successful response

        success : function(json) {
            //console.log(json);
        	results = json.results;
        	total = json.count;
        	cant = cant + results.length;
        	next=json.next;
            var desc="";
            for (var i = 0; i < results.length; i++) {
                elements.push(results[i]);
                dateString = convert_to_readable_date(results[i].added);
                desc = (! results[i].desc) ? results[i].numero : results[i].desc;
                position = results[i].screenshot.lastIndexOf('.');
                thumbnail_name = results[i].screenshot.slice(0,position)+"_th"+results[i].screenshot.slice(position);
                cssclass = ($(window).width()<768) ? 'pure-u-1-2': 'pure-u-1-4';
                $("#denuncias").append('<div class="'+cssclass+'" style="margin-right:1em" title="Denuncia #' +
                    results[i].id+'"> <figure><label>Número:<a href="/buscar/'+results[i].numero+'">' +
                    results[i].numero+'</a></label> <label> Tipo:'+results[i].tipo+'</label> <a href="' +
                    results[i].screenshot+'" target="_blank"><img src="'+thumbnail_name+'" title="'+desc +
                    '" /></a> <figcaption>'+ dateString+'</figcaption></figure>');
        }
            toTable();
            $("#canti").html("Se obtuvieron " +cant+" de "+ total + " denuncias");
            if (!next){
            	$("#botmas").prop('disabled', true);
            	$("#botmas").prop('title', 'No hay mas resultados para cargar');
            }else{
            	$("#denuncias").append('<br><hr><br>');
            }
        },
        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};