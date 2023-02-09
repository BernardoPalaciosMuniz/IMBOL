imscale_f=imcal(500e-6,250e-6);

function scale = imcal(R1,R2)
    folder=uigetdir('/Volumes/IMBOL_A');
    file=dir([folder,'/*.tif']);
    file=[file(1).folder,'/',file(1).name];
    IM=imread(file);
    imshow(IM,[0,2^12])
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
    if r(1,1)>5
        [centers, radii] = imfindcircles(IM,r,'ObjectPolarity','dark');
        viscircles(centers, radii,'EdgeColor','b');
        scale2=R2/mean(radii);
        scale=(scale1+scale2)/2;
    else
        scale=scale1;
    end
    
    

end

function clickCallback(~,evt)

if strcmp(evt.SelectionType,'double')
    uiresume;
end

end