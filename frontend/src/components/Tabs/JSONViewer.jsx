import React from 'react';
import ReactJson from 'react-json-view';
import { useStore } from '../../store/useStore';

const JSONViewer = () => {
    const { currentFile } = useStore();

    return (
        <div className="h-full overflow-y-auto p-4 bg-background">
            <ReactJson
                src={currentFile || {}}
                theme="rjv-default"
                displayDataTypes={false}
                enableClipboard={true}
                style={{ backgroundColor: 'transparent', fontSize: '13px' }}
            />
        </div>
    );
};

export default JSONViewer;
