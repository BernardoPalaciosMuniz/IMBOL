imscale=imcal('/Users/bernardo/Bernardo_Local/backup/thorlabs_R3L3S5P__20220916_171346.tif',500e-6,250e-6);

function scale = imcal(file,R1,R2)
    IM=imread(file);
    imshow(IM,[])
    roi = drawcircle();
    l = addlistener(roi,'ROIClicked',@clickCallback);
    uiwait;
    delete(l);
    r=roi.Radius;
    variance=5;
    r=round([r-variance,r+variance]);
    [centers, radii] = imfindcircles(IM,r,'ObjectPolarity','dark');
    viscircles(centers, radii,'EdgeColor','b');
    scale1=R1/mean(radii);
    roi = drawcircle();
    l = addlistener(roi,'ROIClicked',@clickCallback);
    uiwait;
    delete(l);
    r=roi.Radius;
    variance=4;
    r=round([r-variance,r+variance]);
    [centers, radii] = imfindcircles(IM,r,'ObjectPolarity','dark');
    viscircles(centers, radii,'EdgeColor','b');
    scale2=R2/mean(radii);
    scale=(scale1+scale2)/2;
end

function clickCallback(~,evt)

if strcmp(evt.SelectionType,'double')
    uiresume;
end

end