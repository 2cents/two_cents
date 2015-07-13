(function(obj) {

	var requestFileSystem = obj.webkitRequestFileSystem || obj.mozRequestFileSystem || obj.requestFileSystem;

	function onerror(message) {
		alert(message);
	}

	function createTempFile(callback) {
		var tmpFilename = "tmp.dat";
		requestFileSystem(TEMPORARY, 4 * 1024 * 1024 * 1024, function(filesystem) {
			function create() {
				filesystem.root.getFile(tmpFilename, {
					create : true
				}, function(zipFile) {
					callback(zipFile);
				});
			}

			filesystem.root.getFile(tmpFilename, null, function(entry) {
				entry.remove(create, create);
			}, create);
		});
	}
    
    function readFile(fileList) {//			fileInput.disabled = true;
            var docFile = fileList[0];
            if (docFile.name.match(/\.txt$/g)) {
                var reader = new FileReader();

                reader.onload = function(e) {
                    var text = reader.result;
                    var docFileHtml = document.getElementById("docFileHtml");
                    var docTitle = document.getElementById("docTitle");
                    var title = docFile.name;
                    title = title.replace(/\.txt$/, "");
                    docTitle.value = title;
                    docFileHtml.value = '<span style="white-space:pre">' + text + '</span>';
                }
                reader.readAsText(docFile);
            } else {
                model.getEntries(fileList[0], function(entries) {
    //				fileList.innerHTML = "";
                    entries.forEach(function(entry) {
    //					var li = document.createElement("li");
    //					var a = document.createElement("a");
    //					a.textContent = entry.filename;
                        if (entry.filename == "word/document.xml") {
    //                        alert(entry.filename);
                          entry.getData(new zip.TextWriter(), function(text) {
                            // text contains the entry data as a String

                              if (window.DOMParser)
                              {
                              parser=new DOMParser();
                              xmlDoc=parser.parseFromString(text,"text/xml");
                              }
                            else // Internet Explorer
                              {
                              xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
                              xmlDoc.async=false;
                              xmlDoc.loadXML(text);
                              }
                              collection = xmlDoc.documentElement.querySelectorAll("*");
                                var text = null;
                                var docx = document.createElement("docx");
                                var docTitle = document.getElementById("docTitle");
                                var title = docFile.name;
                                title = title.replace(/\.docx$/, "");
                                title = title.replace(/\.doc$/, "");
                                docTitle.value = title;
                                var docFileHtml = document.getElementById("docFileHtml");
                                for (var i = 0; i < collection.length; i++) {
                                    if (collection[i].tagName == "w:p") {
                                        var par = document.createElement("p");
                                        var parRuns = collection[i].querySelectorAll("*");
                                        for (var j = 0; j < parRuns.length; j++) {
                                            if (parRuns[j].tagName == "w:r") {
                                                var runText = parRuns[j].textContent;
                                                var runBold = false;
                                                var runItalic = false;
                                                var runUnderline = false;
                                                var runTags = parRuns[j].querySelectorAll("*");
                                                var textSize = 0;
                                                for (var k = 0; k < runTags.length; k++) {
                                                    if (!runBold && runTags[k].tagName == "w:b") {
                                                        runBold = true;
                                                    } else if (!runItalic && runTags[k].tagName == "w:i") {
                                                        runItalic = true;
                                                    } else if (!runUnderline && runTags[k].tagName == "w:u") {
                                                        runUnderline = true;
                                                    } else if (runTags[k].tagName == "w:sz") {
                                                        textSize = runTags[k].getAttribute("w:val");
                                                    }


                                                }
                                                var run = document.createElement("span");
                                                run.textContent = runText;
                                //                alert(run);
                                                if (runBold) {
                                                    var inner = run.innerHTML;
                                                    var newInner = "<b>" + inner + "</b>";
                                //                    alert(newInner);
                                                    run.innerHTML = newInner;
                                                }
                                                if (runItalic) {
                                                    var inner = run.innerHTML;
                                                    var newInner = "<i>" + inner + "</i>";
                                                    run.innerHTML = newInner;
                                                }
                                                if (runUnderline) {
                                                    var inner = run.innerHTML;
                                                    var newInner = "<u>" + inner + "</u>";
                                                    run.innerHTML = newInner;
                                                }
                                                if (textSize > 0) {
                                                    run.style.fontSize = textSize + "px";
                                                }
                                                par.appendChild(run);
    //                                            console.log(par.innerHTML);
                                            }

                                        }
                                            text += collection[i].textContent;
                                        docx.appendChild(par);
                                    }
                                }
                                docFileHtml.value = docx.innerHTML;

      //  console.log(text);
                            // close the zip reader

                          }, function(current, total) {
                            // onprogress callback
                          });
                        }
    //					a.href = "#";
    //					a.addEventListener("click", function(event) {
    //						if (!a.download) {
    //							download(entry, li, a);
    //							event.preventDefault();
    //							return false;
    //						}
    //					}, false);
    //					li.appendChild(a);
    //					fileList.appendChild(li);
                    });
                });
            }
        
    }

    
               
  var dropZone = document.getElementById('fileDrop');           

  function handleFileSelect(evt) {
    evt.stopPropagation();
    evt.preventDefault();

    var files = evt.dataTransfer.files; // FileList object.
      dropZone.textContent = files[0].name;
      dropZone.style.color = "#000000";
      
      readFile(files);
  }
        
  function handleDragOver(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
      dropZone.style.backgroundColor = "#E9E9E9";
    
  }
  dropZone.addEventListener('dragover', handleDragOver, false);
  dropZone.addEventListener('drop', handleFileSelect, false);
    
	var model = (function() {
		var URL = obj.webkitURL || obj.mozURL || obj.URL;

		return {
			getEntries : function(file, onend) {
				zip.createReader(new zip.BlobReader(file), function(zipReader) {
					zipReader.getEntries(onend);
				}, onerror);
			},
			getEntryFile : function(entry, creationMethod, onend, onprogress) {
				var writer, zipFileEntry;

				function getData() {
					entry.getData(writer, function(blob) {
						var blobURL = creationMethod == "Blob" ? URL.createObjectURL(blob) : zipFileEntry.toURL();
						onend(blobURL);
					}, onprogress);
				}

				if (creationMethod == "Blob") {
					writer = new zip.BlobWriter();
					getData();
				} else {
					createTempFile(function(fileEntry) {
						zipFileEntry = fileEntry;
						writer = new zip.FileWriter(zipFileEntry);
						getData();
					});
				}
			}
		};
	})();

	(function() {
		var fileInput = document.getElementById("file-input");
		var unzipProgress = document.createElement("progress");
//		var fileList = document.getElementById("file-list");
//		var creationMethodInput = document.getElementById("creation-method-input");

		function download(entry, li, a) {
			model.getEntryFile(entry, "Blob", function(blobURL) {
				var clickEvent = document.createEvent("MouseEvent");
				if (unzipProgress.parentNode)
					unzipProgress.parentNode.removeChild(unzipProgress);
				unzipProgress.value = 0;
				unzipProgress.max = 0;
				clickEvent.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
				a.href = blobURL;
				a.download = entry.filename;
				a.dispatchEvent(clickEvent);
			}, function(current, total) {
				unzipProgress.value = current;
				unzipProgress.max = total;
				li.appendChild(unzipProgress);
			});
		}

		if (typeof requestFileSystem == "undefined")
			creationMethodInput.options.length = 1;
		fileInput.addEventListener('change', function() {
               
            var dropZone = document.getElementById('fileDrop');   
            dropZone.textContent = fileInput.files[0].name;
            dropZone.style.color = "#000000";
            dropZone.style.backgroundColor = "#E9E9E9";
            
//			fileInput.disabled = true;
            var docFile = fileInput.files[0];
            if (docFile.name.match(/\.txt$/g)) {
                var reader = new FileReader();

                reader.onload = function(e) {
                    var text = reader.result;
                    var docFileHtml = document.getElementById("docFileHtml");
                    var docTitle = document.getElementById("docTitle");
                    var title = docFile.name;
                    title = title.replace(/\.txt$/, "");
                    docTitle.value = title;
                    docFileHtml.value = '<span style="white-space:pre">' + text + '</span>';
                }
                reader.readAsText(docFile);
            } else {
                model.getEntries(fileInput.files[0], function(entries) {
    //				fileList.innerHTML = "";
                    entries.forEach(function(entry) {
    //					var li = document.createElement("li");
    //					var a = document.createElement("a");
    //					a.textContent = entry.filename;
                        if (entry.filename == "word/document.xml") {
    //                        alert(entry.filename);
                          entry.getData(new zip.TextWriter(), function(text) {
                            // text contains the entry data as a String

                              if (window.DOMParser)
                              {
                              parser=new DOMParser();
                              xmlDoc=parser.parseFromString(text,"text/xml");
                              }
                            else // Internet Explorer
                              {
                              xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
                              xmlDoc.async=false;
                              xmlDoc.loadXML(text);
                              }
                              collection = xmlDoc.documentElement.querySelectorAll("*");
                                var text = null;
                                var docx = document.createElement("docx");
                                var docTitle = document.getElementById("docTitle");
                                var title = docFile.name;
                                title = title.replace(/\.docx$/, "");
                                title = title.replace(/\.doc$/, "");
                                docTitle.value = title;
                                var docFileHtml = document.getElementById("docFileHtml");
                                for (var i = 0; i < collection.length; i++) {
                                    if (collection[i].tagName == "w:p") {
                                        var par = document.createElement("p");
                                        var parRuns = collection[i].querySelectorAll("*");
                                        for (var j = 0; j < parRuns.length; j++) {
                                            if (parRuns[j].tagName == "w:r") {
                                                var runText = parRuns[j].textContent;
                                                var runBold = false;
                                                var runItalic = false;
                                                var runUnderline = false;
                                                var runTags = parRuns[j].querySelectorAll("*");
                                                var textSize = 0;
                                                for (var k = 0; k < runTags.length; k++) {
                                                    if (!runBold && runTags[k].tagName == "w:b") {
                                                        runBold = true;
                                                    } else if (!runItalic && runTags[k].tagName == "w:i") {
                                                        runItalic = true;
                                                    } else if (!runUnderline && runTags[k].tagName == "w:u") {
                                                        runUnderline = true;
                                                    } else if (runTags[k].tagName == "w:sz") {
                                                        textSize = runTags[k].getAttribute("w:val");
                                                    }


                                                }
                                                var run = document.createElement("span");
                                                run.textContent = runText;
                                //                alert(run);
                                                if (runBold) {
                                                    var inner = run.innerHTML;
                                                    var newInner = "<b>" + inner + "</b>";
                                //                    alert(newInner);
                                                    run.innerHTML = newInner;
                                                }
                                                if (runItalic) {
                                                    var inner = run.innerHTML;
                                                    var newInner = "<i>" + inner + "</i>";
                                                    run.innerHTML = newInner;
                                                }
                                                if (runUnderline) {
                                                    var inner = run.innerHTML;
                                                    var newInner = "<u>" + inner + "</u>";
                                                    run.innerHTML = newInner;
                                                }
                                                if (textSize > 0) {
                                                    run.style.fontSize = textSize + "px";
                                                }
                                                par.appendChild(run);
    //                                            console.log(par.innerHTML);
                                            }

                                        }
                                            text += collection[i].textContent;
                                        docx.appendChild(par);
                                    }
                                }
                                docFileHtml.value = docx.innerHTML;

      //  console.log(text);
                            // close the zip reader

                          }, function(current, total) {
                            // onprogress callback
                          });
                        }
    //					a.href = "#";
    //					a.addEventListener("click", function(event) {
    //						if (!a.download) {
    //							download(entry, li, a);
    //							event.preventDefault();
    //							return false;
    //						}
    //					}, false);
    //					li.appendChild(a);
    //					fileList.appendChild(li);
                    });
                });
            }
		}, false);
	})();

})(this);