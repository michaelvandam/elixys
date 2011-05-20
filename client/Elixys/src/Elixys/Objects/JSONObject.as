/* ---------------------------------------------------------------------------
Author: Manish Jethani (manish.jethani@gmail.com)
Version: 0.1
Date: August 25, 2008

http://manishjethani.com/jsonobject

Copyright (c) 2008 Manish Jethani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
--------------------------------------------------------------------------- */

package Elixys.Objects
{
	import com.adobe.serialization.json.JSON;

	import flash.utils.Proxy;
	import flash.utils.flash_proxy;
	
	/**
	 *  A JSONObject is an object that is capable of populating itself out of a
	 *  JSON-formatted string and converting itself back to a JSON-formatted
	 *  string when required.
	 */
	dynamic public class JSONObject extends Proxy
	{
		private var content:Object;
		private var contentByIndex:Array;
	
		public function JSONObject(data:String = null, existingcontent:Object = null)
		{
			if (data != null)
			{
				content = JSON.decode(data);
			}
			else
			{
				content = existingcontent;
			}
		}
	
		public function populate(data:String):void
		{
			content = JSON.decode(data);
		}
	
		public function toString():String
		{
			return JSON.encode(content);
		}
	
		override flash_proxy function deleteProperty(name:*):Boolean
		{
			return delete content[name];
		}
	
		override flash_proxy function getProperty(name:*):*
		{
			return content[name];
		}
	
		override flash_proxy function hasProperty(name:*):Boolean
		{
			return content.hasOwnProperty(name);
		}
	
		override flash_proxy function nextName(index:int):String
		{
			return contentByIndex[index - 1];
		}
	
		override flash_proxy function nextNameIndex(index:int):int
		{
			if (index == 0) {
				contentByIndex = new Array();
				for (var p:* in content)
					contentByIndex.push(p);
			}
	
			if (index < contentByIndex.length)
				return index + 1;
			else
				return 0;
		}
	
		override flash_proxy function nextValue(index:int):*
		{
			return content[contentByIndex[index - 1]];
		}
	
		override flash_proxy function setProperty(name:*, value:*):void
		{
			content[name] = value;
		}
	}
}
