
imfiles=getImfiles('/Users/bernardo/Bernardo_Local/backup/20221121/bottom/n7000_n7000_12800fps_20221121_175305');

function files = getImfiles(folder)
imgs=dir([folder,'/*.tif']);
files=string(zeros(length(imgs),1));
for i= 1:length(imgs)
    files(i)=[imgs(i).folder,'/',imgs(i).name];
end

end

