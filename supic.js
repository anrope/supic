function ask_google(query, position) {
	var prequery = "https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=";
	$.ajax({
		url: prequery + query,
		dataType: "jsonp",
		success: (function (pos) {
			return function(data) {
				google_callback(data, pos);
			};
		} (position))
	});
}

function google_callback(data, position) {
	if (data) {
		$("#google_response" + position + " > p").html(data.responseData.results[0].title);
		$("#google_response" + position + " > img").attr("src", data.responseData.results[0].url);
	}
}

function ask_flickr(query, position) {
	var flickr_api_key = "28ed3bf372d21044e48fb95fe2c6477d";
	var prequery = "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=" + flickr_api_key + "&format=json&jsoncallback=?&per_page=2&text=";
	$.ajax({
		url: prequery + query,
		dataType: "jsonp",
		success: (function (pos) {
			return function(data) {
				flickr_callback(data, position);
			};
		} (position))
	});
}

function flickr_callback(data, position) {
	if (data) {
		if (data.photos.pages != 0) {
			$("#flickr_response" + position + " > p").html(data.photos.photo[0].title);
			var farmid = data.photos.photo[0].farm;
			var serverid = data.photos.photo[0].server;
			var id = data.photos.photo[0].id;
			var secret = data.photos.photo[0].secret;
			var imgurl = "http://farm" + farmid + ".static.flickr.com/" + serverid + "/" + id + "_" + secret + ".jpg";
			$("#flickr_response" + position + " > img").attr("src", imgurl);
		} else {
			$("#flickr_response" + position + " > p").html("<b><i>No flickr results.</i></b>");
		}
	}
}

function parse_query() {
	$.ajax({
		url: "/parse_query",
		data: {query: $("#twitter_query").val()},
		dataType: "json",
		success: parse_callback
	});
}

function parse_callback(data) {
	if (data.keyterms[0].token == "supic: no tweets") {
		return false;
	}
	for (var i = 0; i < data.keyterms.length; i++) {
		ask_google(data.keyterms[i].token, i + 1);
		ask_flickr(data.keyterms[i].token, i + 1);
		$("#parse_response" + (i + 1) + " > h2").html(data.keyterms[i].token);
	}
}

$(document).ready(function() {
	$(document.body).keyup(function(event) {
		if (event.which == 13) {
			parse_query();
		}
	});
});

// function ask_imgur() {
// 	6a941a68154cbe9160f16f55784d7092
// }

// function ask_twitter() {
// 	var prequery = "http://search.twitter.com/search.json?rpp=1&q=";
// 	var query = $("#twitter_query").val();
// 	$.ajax({
// 		url: prequery + query,
// 		dataType: "jsonp",
// 		jsonpCallback: "twitter_callback"
// 	});
// }

// function twitter_callback(data) {
// 	if (data) {
// 		$("#twitter_response" + current_row + " > h2").html(data.results[0].from_user);
// 		$("#twitter_response" + current_row + " > p").html(data.results[0].text);
// 		var avatar = data.results[0].profile_image_url.replace("_normal", "");
// 		$("#twitter_response" + current_row + " > img").attr("src", avatar);
// 		parse_query();
// 	}
// }