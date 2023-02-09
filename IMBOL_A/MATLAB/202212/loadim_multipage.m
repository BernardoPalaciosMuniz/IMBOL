startframe=1;
% impactframe=271;
endframe=impactframe+350;
if endframe>length(imfinfo(imfiles_f))
    endframe=length(imfinfo(imfiles_f));
end

IS_f=getIS(imfiles_f,startframe:endframe);
fps=getfps(imfiles_f);



function IS=getIS(imfiles,i)


    bitdepth='uint16';
    [rows,cols]=size(imread(imfiles,1));
    nI=length(i);
    IS=zeros([rows,cols,nI],bitdepth);
    for k = 1:nI
        Ik=imread(imfiles,i(k));
        Ik=imgaussfilt(Ik);
        IS(:,:,k) =Ik ;
    end
    FGM=mean(IS,[1 2]);
    factor = mean(FGM)./FGM;
    IS=uint16(double(IS).*factor);
    
    

    
    
%     for k = 1:nI
%         imshow(IS(:,:,k),[0,2^12])
%     end
end

    function fps=getfps(imfiles)
    location=imfiles;
    filename=split(location,'/');
    filename=filename(end);
    fps=split(filename,'fps');
    fps=split(fps(1),'_');
    fps=fps(end);
    fps=str2double(fps(1));
    end
    


    


