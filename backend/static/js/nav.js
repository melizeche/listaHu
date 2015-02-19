load_posts("/api/v1/denuncias/");

var next="";
var cant=0;
var total=0;

function convert_to_readable_date(date_time_string) {
    var newDate = moment(date_time_string).format('MM/DD/YYYY, h:mm:ss a')
    return newDate
}
// Load all posts on page load

function load_posts(url) {
	console.log("hola");
    $.ajax({
        url : url, // the endpoint
        type : "GET", // http method
        // handle a successful response

        success : function(json) {
        	results = json.results
        	total = json.count;
        	//console.log(json.next);
        	cant = cant + results.length;
        	next=json.next;
            for (var i = 0; i < results.length; i++) {
                //console.log(results[i]);
                dateString = convert_to_readable_date(results[i].added);
                if(! results[i].desc){ results[i].desc=results[i].numero;}
                if(screen.width<768){
                	$("#denuncias").append('<div class="pure-u-1-2" style="margin-right:1em" title="Denuncia #'+results[i].id+'"> <figure><label>Número:'+results[i].numero+'</label> <label> Tipo:'+results[i].tipo+'</label> <a href="'+results[i].screenshot+'" target="_blank"><img src="'+results[i].screenshot+'"></a> <figcaption>'+ dateString+'</figcaption></figure>');	
                }else{
                	$("#denuncias").append('<div class="pure-u-1-4" style="margin-right:1em" title="Denuncia #'+results[i].id+'"> <figure><label>Número:'+results[i].numero+'</label> <label> Tipo:'+results[i].tipo+'</label> <a href="'+results[i].screenshot+'" target="_blank"><img src="'+results[i].screenshot+'"></a> <figcaption>'+ dateString+'</figcaption></figure>');
            }	}
            console.log(next);
            $("#canti").html("Se obtuvieron " +cant+" de "+ total + " denuncias");
            if (!next){
            	//console.log('aaaa');
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