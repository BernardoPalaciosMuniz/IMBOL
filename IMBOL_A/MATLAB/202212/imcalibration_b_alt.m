imscale_b=getscale_alt(Dd,IS_b);

function scale_b=getscale_alt(Dd,IS_b)
    IM=IS_b(:,:,1);
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
    D=2*mean(radii);
    scale_b=Dd/D;

end


function clickCallback(~,evt)

if strcmp(evt.SelectionType,'double')
    uiresume;
end

end