import logging

def validate_records(data):

    valid_records = []
    invalid_records = []
    
    seen_ids=set()

    for record in data:
        errors=[]
            
        id_ = record.get('id')
        if id_ is None:                      #id must be present and unique
            errors.append("Missing ID")
        elif id_ in seen_ids:
            errors.append("Duplicate ID")
        else:
            seen_ids.add(id_)

        title = record.get('title')
        if title is None:               #title must be present
            errors.append("Missing Title")

        category = record.get('category')
        if category is None:               #Category must be present
            errors.append("Missing Category")


        price = record.get('price')
        if price is None:        #price must be present & positive & numeric
            errors.append("Invalid price: Missing ")
        elif not isinstance(price, (int, float)):     
            errors.append("Invalid price: not Numeric")
        elif price < 0:
            errors.append("Invalid price: Negative")
                
                     

        rating = record.get('rating', {}).get('rate')
        if rating is None:              #rating:must be present & numeric & btn 0-5  
            errors.append("Invalid rating: Missing")
        elif not isinstance(rating, (int, float)):     
            errors.append("Invalid rating: not Numeric")
        elif rating<0 or rating>5: 
            errors.append("Invalid rating: out of Range")
                    

        #check bad data
        if errors:
            invalid_records.append({"record":record,"errors":errors})
        else:
            valid_records.append(record)

    logging.info(f"{len(valid_records)} valid, {len(invalid_records)} invalid")
    return valid_records, invalid_records