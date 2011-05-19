package Elixys.Objects
{
	import Elixys.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class SequenceMetadata extends JSONObject
	{
		// Constructor
		public function SequenceMetadata(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = m_sDefault;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type() != null) && (Type() != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		/// Copy
		public function Copy(pSourceSequence:SequenceMetadata):void
		{
			super.flash_proxy::setProperty("name", pSourceSequence.Name());
			super.flash_proxy::setProperty("time", pSourceSequence.Time());
			super.flash_proxy::setProperty("date", pSourceSequence.Date());
			super.flash_proxy::setProperty("comment", pSourceSequence.Comment());
			super.flash_proxy::setProperty("id", pSourceSequence.ID());
			super.flash_proxy::setProperty("creator", pSourceSequence.Creator());
			super.flash_proxy::setProperty("operations", pSourceSequence.Operations().toString());
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function Time():String
		{
			return super.flash_proxy::getProperty("time");
		}
		public function Date():String
		{
			return super.flash_proxy::getProperty("date");
		}
		public function Comment():String
		{
			return super.flash_proxy::getProperty("comment");
		}
		public function ID():String
		{
			return super.flash_proxy::getProperty("id");
		}
		public function Creator():String
		{
			return super.flash_proxy::getProperty("creator");
		}
		public function Operations():uint
		{
			return parseInt(super.flash_proxy::getProperty("creator"));
		}

		// Type
		static public var TYPE:String = "sequencemetadata";
		
		// Default format
		private var m_sDefault:String = "{ \"type\":\"sequencemetadata\", \"name\":\"\", \"time\":\"\", \"date\":\"\", " +
			"\"comment\":\"\", \"id\":\"\", \"creator\":\"\", \"operations\":\"\" }";
	}
}
