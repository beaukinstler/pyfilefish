// find_duplicates.js

var MongoClient = require('mongodb').MongoClient,
    commandLineArgs = require('command-line-args'), 
    assert = require('assert');


var options = commandLineOptions();


MongoClient.connect('mongodb://localhost:27017/pyfi', function(err, db) {

    assert.equal(err, null);
    console.log("Successfully connected to MongoDB.");
    
    var query = queryDocument(options);
    var projection = projectionDocument(options);

    var cursor = db.collection(options.collection).find(query);
    cursor.project(projection);
    cursor.sort({Filename:1, Date:-1});

    var numMatches = 0;
    var numOfDups = 0;
    var mark_for_removal = [];
    var previous = {};
    var previous = { Filename:"" ,Hash:"", FileSize:"",Date:"" };
    cursor.forEach(
        


        function(doc) {
            
            numMatches = numMatches + 1;
            //console.log( "CURRENT DOC:" );
            //console.log( doc );
            //console.log( "PREVIOUS: " );
            //console.log( previous);
            if ( (doc.Filename == previous.Filename) && 
                  (doc.Date == previous.Date) &&
                  (doc.Hash == previous.Hash) ){
              console.log("DEBUG: SAME!!!!");
              console.log( "CURRENT DOC:" );
              console.log( doc );
              console.log( "PREVIOUS: " );
              console.log( previous);              
              numOfDups = numOfDups + 1;
              mark_for_removal.push(doc._id);


            }
            previous = doc;
        },
        function(err) {
            assert.equal(err, null);
            console.log("Our query was:" + JSON.stringify(query));
            console.log("Matching documents: " + numMatches);
            console.log("Number of duplicates: " + numOfDups);

            
            console.log("Marked for removal " + mark_for_removal[numOfDups]);


            var filter = {"_id": {"$in":mark_for_removal}};
            db.collection(options.collection).deleteMany(filter, function(err, res) {

              console.log(res.result);
              console.log(mark_for_removal.length + " docs removed from db");
              return db.close();

            });
            
        }
    );    

  console.log(mark_for_removal);
});
  


function queryDocument(options) {

    console.log(options);
    
    var query = {};

    // if ("overview" in options) {
    //     query.overview = {"$regex": options.overview, "$options": "i"};
    // }
    


    return query;
    
}


function projectionDocument(options) {

    var projection = {
        "_id": 1,
        "Filename": 1,
        "Date": 1,
        "FileSize": 1,
        "Hash" :1
    };

    return projection;
}




function commandLineOptions() {

    var cmdl = commandLineArgs([
        { name: "collection", alias: "c", type: String }
    ]);
    
    var options = cmdl.parse()
    if (Object.keys(options).length < 1) {
        console.log(cmdl.getUsage({
            title: "Usage",
            description: "You must provide a collection name. See below."
        }));
        process.exit();
    }

    return options;
    
}


