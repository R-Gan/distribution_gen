// difficulties with printing in console on site
// last statement returns data. copy object, paste into new file in /race_lineups folder
// https://en.netkeiba.com/
// https://en.netkeiba.com/race/shutuba.html?race_id=202609020611

const JST_OFFSET_MINUTES = 9 * 60; // Japan is UTC+9
const TEN_MINUTES_IN_SECONDS = 10 * 60;
const year = new Date().getFullYear();
var dayMonthText = $("dd.Active").find("span.Day01").text(); // appears in form: "15 APR"
var timeText = $(".Race_Data").text().split("\n")[0].trim(); // appear in form: "15:40"


const monthMap = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12
}

// const HONG_KONG_OFFSET_MINUTES = 8 * 60; // Hong Kong is UTC+8

function buildHongKongUnixTimestamp(year, dayMonthText, timeText) {
    const [day, monthText] = dayMonthText.trim().split(" ");
    const [hour, minute] = timeText.trim().split(":").map(Number);
    const month = monthMap[monthText.toUpperCase()];

    if (!month) {
        throw new Error(`Unrecognized month abbreviation: ${monthText}`);
    }

    // Date.UTC treats the inputs as UTC. 
    // To get the real UTC time, we subtract the JST offset (9 hours).
    const utcMillis = Date.UTC(
        Number(year),
        month - 1,
        Number(day),
        hour,
        minute
    ) - (JST_OFFSET_MINUTES * 60 * 1000);

    const unixTimestamp = Math.floor(utcMillis / 1000);

    return unixTimestamp - TEN_MINUTES_IN_SECONDS;
}

const unixTimestamp = buildHongKongUnixTimestamp(year, dayMonthText, timeText);
unixTimestamp;

