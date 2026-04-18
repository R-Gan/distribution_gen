// https://jra.jp/JRADB/accessS.html?CNAME=pw01sde1009202602041120260405/9D
// issue with different spellings between netkeiba and jra, e.g. "Croix duNord" vs "Croix du Nord"
// just use this as a reference and correct spellings manually after saving new file to /live_results folder

var horses = [];
var horseElems = $("td.horse");
horseElems.each(function(index, val){
  horses.push($(val).find("a").text())
});

var outputObj = {
  "results": horses
};

outputObj;