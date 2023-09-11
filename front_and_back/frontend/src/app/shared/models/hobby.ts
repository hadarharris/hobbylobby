export class Hobby{
  hobbyImageMapping: { [key: string]: string } = {
    'sport': 'ball.png',
    'food': 'food.png',
    'cook': 'food.png',
    'recipe': 'food.png',
    'music': 'music.png',
    'book': 'book.png',
    'art': 'art.png',
    'painting': 'art.png',
    'drawing': 'art.png', 
    'animal': 'animal.png',
    'pet':'animal.png',
    'gym': 'gym.png',
    'beach': 'beach.png',
    'movie': 'movie.png',
    'travel': 'travel.png',
    'gardene': 'garden.png',
    'puzzle': 'puzzle.png',
    'yoga': 'yoga.png',
    'museum': 'museum.png',
    'photo': 'photo.png',
    'camera': 'photo.png',
    'nature': 'camp.png',
    'garden': "garden.png",
    'basketball': "basketball.png",
    'cooking': 'cook.png', // Image for the "cooking" key
    'history': 'museum.png', // Image for the "history buff" key
    'outdoor': 'beach.png', // Image for the "outdoors" key
    'language': 'book.png', // Image for the "language enthusiast" key
    'musician': 'music.png', // Image for the "musician" key
    'write': 'book.png', // Image for the "writer" key
    'baking': 'food.png', // Image for the "baking" key
    'TV': 'movie.png', // Image for the "binge-watching TV shows" key
    'dinner': 'cook.png', // Image for the "cooking dinner" key
    'dancing': 'dance.png', // Image for the "dancing" key
    'dance': 'dance.png',
    'picnic': 'food.png', // Image for the "picnics" key
    'trip': 'travel.png', // Image for the "road trips" key
    'park': 'ball.png', // Image for the "amusement parks" key
    'sunset': 'beach.png', // Image for the "beach sunset" key
    'hike': 'travel.png', // Image for the "hiking in the mountains" key
    'hiking': 'travel.png',
    'board game': 'puzzle.png', // Image for the "board games" key
    'film': 'movie.png', // Image for the "film buff" key
    'fitness': 'fitness.png', // Image for the "fitness routines" key
    'DIY': 'friends2.png', // Image for the "DIY home improvement" key
    'craft': 'friends2.png',
    'literature': 'book.png', // Image for the "literature lover" key
    'paint': 'art.png', // Image for the "painter" key
    'thrill-seeker': 'extreme.png', // Image for the "thrill-seeker" key,
    'adventure':'travel.png',
    'fashion': 'fashion.png', // Image for the "vintage fashion collector" key
    'vinyl records': 'music.png', // Image for the "vinyl records collector" key
    'ball': 'ball.png', // Image for the "sports fan" key
    'comic': 'book.png', // Image for the "comic book enthusiast" key
    'junkie': 'extreme.png', // Image for the "adrenaline junkie" key
    'adrenaline': 'extreme.png', // Image for the "adrenaline activities" key
    'read': 'book.png', // Image for the "avid reader" key
    'knitting': 'knitting.png', // Image for the "knitting" key
    'gardening': 'garden.png', // Image for the "gardening" key
    'green': 'garden.png', // Image for the "green thumb" key
    'shelter': 'animal.png', // Image for the "animal shelter volunteer" key
    'boardgame': 'puzzle.png', // Image for the "board game enthusiast" key
    'video game': 'gaming.png', // Image for the "video game player" key
    'card game enthusiast': 'board.png', // Image for the "card game enthusiast" key
    'chess': 'board.png', // Image for the "chess player" key
    'golf': 'ball.png', // Image for the "golf enthusiast" key
    'instrument': 'music.png', // Image for the "musical instruments" key
    'science': 'book.png', // Image for the "science exploration" key
    'extreme': 'extreme.png', // Image for the "extreme sports" key
    'writing': 'book.png', // Image for the "writing" key
    'calligraphy': 'art.png', // Image for the "calligraphy" key
    'martial arts': 'martialarts.png', // Image for the "martial arts" key
    'meditation': 'yoga.png', 
    'running': 'fit.png', // Image for the "running" key
    'run': 'fit.png',
    'car': 'car.png',
    'computer': 'computer.png',
    'internet': 'computer.png',
    'programming': 'computer.png',
    'tech':'computer.png',
    'camp':'camp.png',
    'fish':'fishing.png',
    'cards':'cards.png',
    'poker':'cards.png',
    'show':'show.png',
    'performance':'show.png',
    'concert':'show.png',
    'stage':'show.png',
    'sing':'show.png',
    'festival':'show.png',
    'coffee':'coffee.png',
    'drink':'coffee.png',
    'hot drink':'coffee.png',
    'vintage':'vintage.png',
    'collect':'vintage.png',
    'old':'vintage.png',
    'cloth':'fashion.png',
    'accessories':'fashion.png',
    'comedy':'show.png',
    'comedian':'show.png'
  };

  getHobbyImage(hobby: string): string {
    // Check if the hobby contains a keyword from the mapping; otherwise, use a default image
    for (const keyword in this.hobbyImageMapping) {
      if (hobby.toLowerCase().includes(keyword.toLowerCase())) {
        return this.hobbyImageMapping[keyword];
      }
    }
    return 'logo.png'; // Default image if no keyword matches
  }
}

