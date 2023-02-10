clear IS;


[filename,fps,IS,BG]=getIS(imfiles,155:255);

function [filename,fps,IS,BG]=getIS(imfiles,i)

    filename=imfiles(i(1));
    info = imfinfo(filename);
%     nI = length(info);
    
    bitdepth=info.BitDepth;
    if bitdepth>8
        bitdepth='uint16';
    else
        bitdepth='uint8';
    end
    [rows,cols]=size(imread(filename));
    nI=length(i);
    IS=zeros([rows,cols,nI],bitdepth);
    for k = 1:nI
        Ik=imread(imfiles(i(k)));
        Ik=imgaussfilt(Ik);
        IS(:,:,k) =Ik ;
    end
    FGM=mean(IS,[1 2]);
    factor = mean(FGM)./FGM;
    IS=uint16(double(IS).*factor);
%     BG=imread(imfiles(i(1)-1));
    BG=zeros([rows,cols,20],bitdepth);
    for k=1:20
        BG(:,:,k)=imread(imfiles(i(1)-k-10));
    end
    FGM=mean(BG,[1 2]);
    factor = mean(FGM)./FGM;
    BG=uint16(double(BG).*factor);
    
    for k = 1:nI
        imshow(IS(:,:,k),[0,2^12])
    end
    conditions=split(filename(end),'_');
    conditions=conditions(conditions~="");
    fps=split(conditions(4),'fps');
    fps=str2double(fps(1));
    
    

end