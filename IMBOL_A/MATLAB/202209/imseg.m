[yU,yR]=segment(IS(:,:,:));

function [yU,yR]=segment(IS)
    FG=min(IS,[],3);
    imshow(FG,[0,2^12])
    roi = drawline();
    pos=roi.Position;
    y1 = pos(1,2); y2 = pos(2,2);
    yU=round((y1+y2)/2);
    roiR = drawline();
    posR=roiR.Position;
    y3 = posR(1,2); y4 = posR(2,2);
    yR=round((y3+y4)/2);
    
end
