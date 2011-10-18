package Elixys.Objects
{
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
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		/// Copy
		public function Copy(pSourceSequence:SequenceMetadata):void
		{
			Name = pSourceSequence.Name;
			Time = pSourceSequence.Time;
			Date = pSourceSequence.Date;
			Comment = pSourceSequence.Comment;
			ID = pSourceSequence.ID;
			Creator = pSourceSequence.Creator;
			Operations = pSourceSequence.Operations;
		}
		
		// Data wrappers
		public function get Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function set Type(value:String):void
		{
			super.flash_proxy::setProperty("type", value);
		}
		
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function set Name(value:String):void
		{
			super.flash_proxy::setProperty("name", value);
		}

		public function get Time():String
		{
			return super.flash_proxy::getProperty("time");
		}
		public function set Time(value:String):void
		{
			super.flash_proxy::setProperty("time", value);
		}
		
		public function get Date():String
		{
			return super.flash_proxy::getProperty("date");
		}
		public function set Date(value:String):void
		{
			super.flash_proxy::setProperty("date", value);
		}

		public function get Comment():String
		{
			return super.flash_proxy::getProperty("comment");
		}
		public function set Comment(value:String):void
		{
			super.flash_proxy::setProperty("comment", value);
		}

		public function get ID():uint
		{
			return super.flash_proxy::getProperty("id");
		}
		public function set ID(value:uint):void
		{
			super.flash_proxy::setProperty("id", value);
		}

		public function get Creator():String
		{
			return super.flash_proxy::getProperty("creator");
		}
		public function set Creator(value:String):void
		{
			super.flash_proxy::setProperty("creator", value);
		}

		public function get Operations():uint
		{
			return parseInt(super.flash_proxy::getProperty("operations"));
		}
		public function set Operations(value:uint):void
		{
			super.flash_proxy::setProperty("operations", value);
		}

		// Type
		static public var TYPE:String = "sequencemetadata";
		
		// Default format
		private var m_sDefault:String = "{ \"type\":\"sequencemetadata\", \"name\":\"\", \"time\":\"\", \"date\":\"\", " +
			"\"comment\":\"\", \"id\":\"\", \"creator\":\"\", \"operations\":\"\" }";
	}
}
