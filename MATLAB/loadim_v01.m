clear IS;
[filename,fps,IS]=getIS(imfiles,filenum);

function [filename,fps,IS]=getIS(imfiles,i)

    filename=imfiles(i);
    info = imfinfo(filename);
%     nI = length(info);
    nI = 400;
    bitdepth=info(1).BitDepth;
    if bitdepth>8
        bitdepth='uint16';
    else
        bitdepth='uint8';
    end
    [rows,cols]=size(imread(filename, 1));
    IS=zeros([rows,cols,nI],bitdepth);
    for k = 1 : nI
        IS(:,:,k) = imread(filename, k);
    end
    
    conditions=split(filename(end),'_');
    conditions=conditions(conditions~="");
    fps=split(conditions(3),'fps');
    fps=str2double(fps(1));
    
    

end