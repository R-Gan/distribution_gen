// difficulties with printing in console on site
// last statement returns data. copy object, paste into new file in /race_lineups folder
// https://en.netkeiba.com/
// https://en.netkeiba.com/race/shutuba.html?race_id=202607010611

const links = $(".HorseLink a").toArray();

var data = {};
var names = "";
var odds = "";
for (var i = 0; i < links.length; i++) {
    var horseName = links[i].innerText;
    var oddsText = $(links[i]).closest(".HorseList").find(".Popular").find("span").text();
    var favoriteText = $(links[i]).closest(".HorseList").find(".Fav").find("span").text();
    data[horseName] = {odds: oddsText, favorite: favoriteText};
}
data;