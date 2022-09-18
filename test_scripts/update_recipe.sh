#!/bin/bash
curl -i \
    -H "Content-Type: application/json" \
    --request 'PUT' \
    --data '{
        "name": "supernoodles",
        "ingredients": [
            { "name": "supernoodle packet", "quantity": { "value": 1, "unit": "item" } }
        ],
        "instructions": [
            "Boil kettle",
            "Open packet and put noodles in a pot .",
            "Open flavouring sache and tip into pot.",
            "Boil for 5 minutes.",
            "Serve"
        ],
        "source": "https://www.iceland.co.uk/p/batchelors-super-noodles-chicken-flavour-90g/56499.html",
        "rating": 0,
        "img": [
            "https://assets.iceland.co.uk/i/iceland/batchelors_super_noodles_chicken_flavour_90g_56499_T1.jpg?$pdpzoom$"
        ],
        "keywords": ["student", "quick", "easy", "fun"],
        "slug": "supernoodles"
    }' \
    'http://localhost:5000/recipes/supernoodles'