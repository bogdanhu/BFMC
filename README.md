# BFMC
boschApp

https://www.dropbox.com/s/83slf9sgkyelphc/demo2.avi?dl=0

# Am eliminat  
binarization2, MinV = perspective_transform(binarization)
cv2.imshow("Binarizare2", binarization2)

    edges = cv2.Canny(gray, 75, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

    # cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    
    
