window.HITSTER_APP_LOADED = true;

const songs = [
  { title: "Bing Crosby - White Christmas", year: 1942, query: "Bing Crosby White Christmas" },
  { title: "Glenn Miller - In the Mood", year: 1939, query: "Glenn Miller In the Mood" },
  { title: "The Ink Spots - If I Didn't Care", year: 1939, query: "The Ink Spots If I Didn't Care" },
  { title: "Édith Piaf - La Vie En Rose", year: 1947, query: "Edith Piaf La Vie En Rose" },
  { title: "Nat King Cole - Mona Lisa", year: 1950, query: "Nat King Cole Mona Lisa" },
  { title: "Elvis Presley - Hound Dog", year: 1956, query: "Elvis Presley Hound Dog" },
  { title: "Chuck Berry - Johnny B. Goode", year: 1958, query: "Chuck Berry Johnny B Goode" },
  { title: "The Platters - Only You", year: 1955, query: "The Platters Only You" },
  { title: "The Beatles - She Loves You", year: 1963, query: "The Beatles She Loves You" },
  { title: "The Rolling Stones - Paint It Black", year: 1966, query: "The Rolling Stones Paint It Black" },
  { title: "Aretha Franklin - Respect", year: 1967, query: "Aretha Franklin Respect" },
  { title: "Simon & Garfunkel - Mrs. Robinson", year: 1968, query: "Simon and Garfunkel Mrs Robinson" },
  { title: "Led Zeppelin - Stairway to Heaven", year: 1971, query: "Led Zeppelin Stairway to Heaven" },
  { title: "ABBA - Dancing Queen", year: 1976, query: "ABBA Dancing Queen" },
  { title: "Bee Gees - Stayin' Alive", year: 1977, query: "Bee Gees Stayin Alive" },
  { title: "Queen - Another One Bites the Dust", year: 1980, query: "Queen Another One Bites the Dust" },
  { title: "a-ha - Take On Me", year: 1984, query: "a-ha Take On Me" },
  { title: "Whitney Houston - I Wanna Dance with Somebody", year: 1987, query: "Whitney Houston I Wanna Dance with Somebody" },
  { title: "Madonna - Like a Prayer", year: 1989, query: "Madonna Like a Prayer" },
  { title: "Nirvana - Smells Like Teen Spirit", year: 1991, query: "Nirvana Smells Like Teen Spirit" },
  { title: "TLC - No Scrubs", year: 1999, query: "TLC No Scrubs" },
  { title: "Britney Spears - ...Baby One More Time", year: 1998, query: "Britney Spears Baby One More Time" },
  { title: "OutKast - Hey Ya!", year: 2003, query: "OutKast Hey Ya" },
  { title: "Beyoncé - Crazy In Love", year: 2003, query: "Beyonce Crazy In Love" },
  { title: "Rihanna - Umbrella", year: 2007, query: "Rihanna Umbrella" },
  { title: "Lady Gaga - Bad Romance", year: 2009, query: "Lady Gaga Bad Romance" },
  { title: "Adele - Rolling in the Deep", year: 2010, query: "Adele Rolling in the Deep" },
  { title: "Mark Ronson ft. Bruno Mars - Uptown Funk", year: 2014, query: "Uptown Funk Mark Ronson Bruno Mars" },
  { title: "Luis Fonsi - Despacito", year: 2017, query: "Luis Fonsi Despacito" },
  { title: "Dua Lipa - Don't Start Now", year: 2019, query: "Dua Lipa Don't Start Now" },
  { title: "The Weeknd - Blinding Lights", year: 2020, query: "The Weeknd Blinding Lights" },
  { title: "Harry Styles - As It Was", year: 2022, query: "Harry Styles As It Was" }
];

const MAX_ROUNDS = 5;
const CLIENT_ID_STORAGE_KEY = "hitster_spotify_client_id";

const drawSongBtn = document.getElementById("drawSongBtn");
const gameArea = document.getElementById("gameArea");
const summaryArea = document.getElementById("summaryArea");
const songTitle = document.getElementById("songTitle");
const spotifyDirectLink = document.getElementById("spotifyDirectLink");
const yearGuess = document.getElementById("yearGuess");
const checkBtn = document.getElementById("checkBtn");
const resultText = document.getElementById("resultText");
const roundText = document.getElementById("roundText");
const scoreText = document.getElementById("scoreText");
const summaryText = document.getElementById("summaryText");
const restartBtn = document.getElementById("restartBtn");
const clientIdInput = document.getElementById("clientIdInput");
const saveClientIdBtn = document.getElementById("saveClientIdBtn");
const clientIdStatus = document.getElementById("clientIdStatus");
const libraryInfo = document.getElementById("libraryInfo");

let currentSong = null;
let round = 0;
let score = 0;
let canCheckGuess = false;
let bag = [];

function toSpotifyOpenSearch(query) {
  return `https://open.spotify.com/search/${encodeURIComponent(query)}`;
}

function refillBag() {
  bag = [...songs];
}

function pickRandomSong() {
  if (bag.length === 0) {
    refillBag();
  }

  const index = Math.floor(Math.random() * bag.length);
  const [picked] = bag.splice(index, 1);
  return picked;
}

function pointsFromDiff(diff) {
  if (diff === 0) return 3;
  if (diff <= 2) return 2;
  if (diff <= 5) return 1;
  return 0;
}

function updateStatus() {
  roundText.textContent = `${round} / ${MAX_ROUNDS}`;
  scoreText.textContent = `${score}`;
}

function updateLibraryInfo() {
  const years = songs.map((song) => song.year);
  const oldest = Math.min(...years);
  const newest = Math.max(...years);
  libraryInfo.textContent = `Kappalekirjasto: ${songs.length} biisiä (${oldest}-${newest}).`;
}

function loadClientIdFromStorage() {
  const savedClientId = localStorage.getItem(CLIENT_ID_STORAGE_KEY);

  if (!savedClientId) {
    clientIdStatus.textContent = "Client ID:tä ei ole vielä tallennettu selaimeen.";
    return;
  }

  clientIdInput.value = savedClientId;
  clientIdStatus.textContent = "Client ID ladattu selaimen muistista.";
}

function saveClientId() {
  const clientId = clientIdInput.value.trim();

  if (!clientId) {
    clientIdStatus.textContent = "Anna ensin Client ID.";
    return;
  }

  localStorage.setItem(CLIENT_ID_STORAGE_KEY, clientId);
  clientIdStatus.textContent = "Client ID tallennettu selaimeen onnistuneesti.";
}

function drawSong() {
  if (round >= MAX_ROUNDS) {
    resultText.textContent = "Peli on päättynyt. Aloita uusi peli.";
    return;
  }

  currentSong = pickRandomSong();
  songTitle.textContent = currentSong.title;
  spotifyDirectLink.href = toSpotifyOpenSearch(currentSong.query);
  yearGuess.value = "";
  resultText.textContent = "";
  canCheckGuess = true;
  gameArea.classList.remove("hidden");
  yearGuess.focus();
}

function finishGame() {
  summaryText.textContent = `Sait ${score} pistettä ${MAX_ROUNDS} kierroksella.`;
  summaryArea.classList.remove("hidden");
  drawSongBtn.disabled = true;
  checkBtn.disabled = true;
}

function checkGuess() {
  if (!currentSong || !canCheckGuess) {
    resultText.textContent = "Arvo ensin kappale.";
    return;
  }

  const guess = Number(yearGuess.value);

  if (!Number.isInteger(guess)) {
    resultText.textContent = "Syötä vuosiluku numerona.";
    return;
  }

  const diff = Math.abs(guess - currentSong.year);
  const points = pointsFromDiff(diff);
  round += 1;
  score += points;
  canCheckGuess = false;

  if (points === 3) {
    resultText.textContent = `Täydellinen osuma! +3 pistettä. Oikea vuosi on ${currentSong.year}.`;
  } else if (points === 2) {
    resultText.textContent = `Lähellä! +2 pistettä. Oikea vuosi on ${currentSong.year}.`;
  } else if (points === 1) {
    resultText.textContent = `Ihan hyvä! +1 piste. Oikea vuosi on ${currentSong.year}.`;
  } else {
    resultText.textContent = `Ei osumaa tällä kertaa. +0 pistettä. Oikea vuosi on ${currentSong.year}.`;
  }

  updateStatus();

  if (round >= MAX_ROUNDS) {
    finishGame();
  }
}

function restartGame() {
  round = 0;
  score = 0;
  currentSong = null;
  canCheckGuess = false;
  gameArea.classList.add("hidden");
  summaryArea.classList.add("hidden");
  drawSongBtn.disabled = false;
  checkBtn.disabled = false;
  spotifyDirectLink.href = "#";
  songTitle.textContent = "-";
  yearGuess.value = "";
  resultText.textContent = "";
  refillBag();
  updateStatus();
}

refillBag();
updateStatus();
updateLibraryInfo();
loadClientIdFromStorage();
drawSongBtn.addEventListener("click", drawSong);
checkBtn.addEventListener("click", checkGuess);
restartBtn.addEventListener("click", restartGame);
saveClientIdBtn.addEventListener("click", saveClientId);
