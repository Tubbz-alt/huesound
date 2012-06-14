var sp = getSpotifyApi(1);

exports.init = init;

function init() 
{
    console.log("init()");

    var models = sp.require('sp://import/scripts/api/models');
    console.log(models.session.country);
}
