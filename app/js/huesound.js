var sp = getSpotifyApi(1);
var models, views;

exports.init = init;
function init() 
{
    models = sp.require('sp://import/scripts/api/models');
    views = sp.require("sp://import/scripts/api/views");
    coverHack.init(models.session.country);
}

mbalbums = function(data) 
{
    coverHack.processCovers(data);
};

coverHack = {
    allColors: ['#000000', '#CC3333', '#FF3333', '#FF6633', '#FF9933', '#FFCC66', '#FFFF33', '#CCCC33', '#99CC33', '#33CC33', '#009933', '#006633', '#33CC99', '#33CCFF', '#3366CC', '#333399', '#000066', '#663399', '#990099', '#990066', '#FF0066', '#CCCC99', '#996666', '#996633', '#663333', '#CC9966', '#996633', '#663300', '#333300', '#330000', '#333333', '#666666'],
    // 30 gives us a 6x5 grid, looks nice
    albumCount: 30,
    firstRun: true,
    processing: false,
    local: false,
    imgUrlBase: "",
    albumAPI: "",
    data: null,
    albumClicked : false,
    fetchCovers: function(color) {
            if(coverHack.firstRun) {
                    $( "#instructions_txt" ).toggle( 'puff', {}, 500, function() {
                            $( "#albumsContainer" ).show();
                    } );
                    coverHack.firstRun = false;
            } else if(!coverHack.processing) {
                    coverHack.view.hideAlbums();
            } else {
                    return;
            }
            coverHack.view.changeBG(color);
            color = color.replace('#', '');
            coverHack.processing = true;
            $.ajax({
                    url: coverHack.albumAPI.replace(/%color%/, color),
                    timeout: 5000,
                    dataType: "jsonp",
                    jsonp: false,
                    jsonpCallback: "mbalbums",
                    cache: false
            });
    },
    processCovers: function(data) {
            var tracks = [], i, j = 0;

            coverHack.processing = false;
            coverHack.data = data;
            coverHack.view.showAlbums();

            for(i = 0; i < coverHack.data.length; i++) 
                coverHack.view.showPlay(i);
    },
    util: {
            // http://stackoverflow.com/questions/1507931/generate-lighter-darker-color-in-css-using-javascript
            color: {
                    pad: function(num, totalChars) {
                        var pad = '0';
                        num = num + '';
                        while (num.length < totalChars) {
                            num = pad + num;
                        }
                        return num;
                    },

                    // Ratio is between 0 and 1
                    changeColor: function(color, ratio, darker) {
                        // Trim trailing/leading whitespace
                        color = color.replace(/^\s*|\s*$/, '');

                        // Expand three-digit hex
                        color = color.replace(
                            /^#?([a-f0-9])([a-f0-9])([a-f0-9])$/i,
                            '#$1$1$2$2$3$3'
                        );

                        // Calculate ratio
                        var difference = Math.round(ratio * 256) * (darker ? -1 : 1),
                            // Determine if input is RGB(A)
                            rgb = color.match(new RegExp('^rgba?\\(\\s*' +
                                '(\\d|[1-9]\\d|1\\d{2}|2[0-4][0-9]|25[0-5])' +
                                '\\s*,\\s*' +
                                '(\\d|[1-9]\\d|1\\d{2}|2[0-4][0-9]|25[0-5])' +
                                '\\s*,\\s*' +
                                '(\\d|[1-9]\\d|1\\d{2}|2[0-4][0-9]|25[0-5])' +
                                '(?:\\s*,\\s*' +
                                '(0|1|0?\\.\\d+))?' +
                                '\\s*\\)$', 'i')),
                            alpha = !!rgb && rgb[4] !== null ? rgb[4] : null,

                            // Convert hex to decimal
                            decimal = !!rgb? [rgb[1], rgb[2], rgb[3]] : color.replace(
                                /^#?([a-f0-9][a-f0-9])([a-f0-9][a-f0-9])([a-f0-9][a-f0-9])/i,
                                function() {
                                    return parseInt(arguments[1], 16) + ',' +
                                        parseInt(arguments[2], 16) + ',' +
                                        parseInt(arguments[3], 16);
                                }
                            ).split(/,/),
                            returnValue;

                        // Return RGB(A)
                        return !!rgb ?
                            'rgb' + (alpha !== null ? 'a' : '') + '(' +
                                Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[0], 10) + difference, darker ? 0 : 255
                                ) + ', ' +
                                Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[1], 10) + difference, darker ? 0 : 255
                                ) + ', ' +
                                Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[2], 10) + difference, darker ? 0 : 255
                                ) +
                                (alpha !== null ? ', ' + alpha : '') +
                                ')' :
                            // Return hex
                            [
                                '#',
                                coverHack.util.color.pad(Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[0], 10) + difference, darker ? 0 : 255
                                ).toString(16), 2),
                                coverHack.util.color.pad(Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[1], 10) + difference, darker ? 0 : 255
                                ).toString(16), 2),
                                coverHack.util.color.pad(Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[2], 10) + difference, darker ? 0 : 255
                                ).toString(16), 2)
                            ].join('');
                    },
                    lighterColor: function(color, ratio) {
                        return coverHack.util.color.changeColor(color, ratio, false);
                    },
                    darkerColor: function(color, ratio) {
                        return coverHack.util.color.changeColor(color, ratio, true);
                    }
            }
    },
    view: {
            albumTpl: '<li id="%i%"><img src="spotify:image:%image_id%" onclick="coverHack.album_clicked(%i%)"></li>',
            showAlbums: function() {
                    $("#progress" ).hide();
                    var i,
                            album,
                            tpl,
                            albumsHTML = [];
                    for(i = 0; i < coverHack.data.length; i++) {
                            album = coverHack.data[i];
                            tpl = coverHack.view.albumTpl;
                            tpl = tpl.replace(/%image_id%/g, album.image_id);
                            tpl = tpl.replace(/%i%/g, i);
                            tpl = tpl.replace(/%id%/g, album.album_uri);
                            albumsHTML.push(tpl);
                    }
                    // insert albums into page
                    $('#albums').html(albumsHTML.join(''));
            },
            hideAlbums: function() {
                    $("#progress").show();
                    // loop through albums and hide them all, one after another
                    $('#albums li').each( function(i, album) {
                            $(album).remove();
                    });
            },
            changeBG: function(color) {
                    color = coverHack.util.color.lighterColor(color, 0.6);
                    $('body').animate( { backgroundColor: color }, 1000);
            },
            showPlay: function(albumIndex) {
                    var albumCover = $('#albums #' + albumIndex);
                    albumCover.data('album_uri', coverHack.data[albumIndex].album_uri);
                    albumCover.addClass('play');
                    albumCover.append('<div class="playbtn"></div>');
                    $('.playbtn', albumCover).fadeIn(500);
            },
            createColorWheel: function() {
                    var r = Raphael("color-wheel");
                    var pie = r.g.piechart(200, 310, 150, [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], {colors: coverHack.allColors});
                    pie.hover(function () {
                            this.sector.stop();
                            this.sector.scale(1.1, 1.1, this.cx, this.cy);
                            if (this.label) {
                                    this.label[0].stop();
                                    this.label[0].scale(1.5);
                                    this.label[1].attr({"font-weight": 800});
                            }
                    }, function () {
                            this.sector.animate({scale: [1, 1, this.cx, this.cy]}, 500, "bounce");
                            if (this.label) {
                                    this.label[0].animate({scale: 1}, 500, "bounce");
                                    this.label[1].attr({"font-weight": 400});
                            }
                    });
                    pie.click(function() {
                            coverHack.fetchCovers(this.sector.attrs.fill);
                    });
            }
    },
    album_clicked: function(index) {
        album_uri = coverHack.data[index].album_uri;
        window.location.href = album_uri;
        albumClicked = true;
    },
    play_clicked: function(album_uri) {
        models.Album.fromURI(album_uri, function(album) 
        {
            models = sp.require("sp://import/scripts/api/models");
            player = models.player;
            player.play(album.tracks[0], album, 0);
        });
    },
    init: function(country) {
            coverHack.view.createColorWheel();
            coverHack.albumAPI = "http://huesound.mbsandbox.org/%color%/" + coverHack.albumCount + "/" + country + "/j";
            $('.play', $('#albums')).live("click", function(e) {
                if (!albumClicked)
                    coverHack.play_clicked($(this).data('album_uri'));
                albumClicked = false;
            });
            $('#play').attr("src", "");
    }
};
