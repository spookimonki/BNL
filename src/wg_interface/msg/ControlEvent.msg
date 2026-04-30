std_msgs/Header header
uint8       control_type        #   Hvilken type signal du sender
float64     right_cycle         #   prosent hvor mye av maks frekvens (hel prosent 50% = 50)
uint8       right_direction     #   tall som representerer retningen på motoren 0, 1
float64     left_cycle          #   prosent hvor mye av maks frekvens (hel prosent 50% = 50)
uint8       left_direction      #   tall som representerer retningen på motoren 0, 1
float64     combined_cycle      #   prosent hvor mye av maks frekvens (hel prosent 50% = 50)
uint8       combined_direction  #   tall som representerer retning 0, 1
uint8       combined_rotation   #   0 = mot klokka, 1 = med klokka